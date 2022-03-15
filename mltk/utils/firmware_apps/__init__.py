import logging
import os 
import yaml 
import bincopy

from mltk.core import TfliteModel
from mltk.cli import  is_command_active
from mltk.utils import commander
from mltk.utils.system import iso_time_str
from mltk.utils.path import create_tempdir
from mltk.utils.archive_downloader import download_verify_extract


def add_image(
    name:str, 
    platform:str,
    accelerator:str,
    url:str, 
    sha1_hash:str,
    logger:logging.Logger
):
    """Add a firmware image to the download_urls.yaml file
    
    Args:
        name: Name of image
        platform: Embedded platform name
        accelerator: Name of hardware accelerator built into image
        url: Download URL
        sha1_hash: SHA1 hash of downloaded file
        logger: Logger
    """
    curdir = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    download_urls_file = f'{curdir}/download_urls.yaml'

    try:
        with open(download_urls_file, 'r') as fp:
            download_urls = yaml.load(fp, Loader=yaml.SafeLoader)
            if not download_urls:
                raise Exception()
    except:
        download_urls = {}

    key = get_url_key(
        name=name, 
        platform=platform, 
        accelerator=accelerator
    )

    download_urls[key] = dict( 
        url=url, 
        sha1=sha1_hash,
        date=iso_time_str()
    )

    with open(download_urls_file, 'w') as fp:
        yaml.dump(download_urls, fp, Dumper=yaml.SafeDumper)

    logger.info(f'Updated {download_urls_file}')


def get_image(
    name:str, 
    platform: str,
    accelerator: str,
    logger:logging.Logger
) -> str:
    """Return the path to a firmware image"""

    curdir = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    download_urls_file = f'{curdir}/download_urls.yaml'
    key = get_url_key(
        name=name, 
        platform=platform, 
        accelerator=accelerator
    )

    try:
        with open(download_urls_file, 'r') as fp:
            download_urls = yaml.load(fp, Loader=yaml.SafeLoader)
    except Exception as e:
        # pylint: disable=raise-missing-from
        raise Exception(f'Failed to load: {download_urls_file}, err: {e}') 

    if not download_urls or key not in download_urls:
        raise RuntimeError(f'Firmware image: {key} not found in {download_urls_file}')

    image_info = download_urls[key]
    download_dir = download_verify_extract(
        url=image_info['url'],
        file_hash=image_info['sha1'],
        file_hash_algorithm='sha1',
        dest_subdir=f'firmware/{key}',
        show_progress=is_command_active(),
        logger=logger,
    )

    img_ext = get_image_extension(platform=platform)
    return f'{download_dir}/{key}{img_ext}'


def program_image_with_model(
    name:str,
    accelerator:str,
    tflite_model:TfliteModel,
    logger: logging.Logger,
    platform:str=None,
    halt:bool = False,
    firmware_image_path:str = None
):
    """Program a FW image + .tflite model to an embedded device"""
    if not platform:
        platform = commander.query_platform()
    
    tflite_name = tflite_model.filename or f'{name}.tflite'
    tmp_tflite_path = create_tempdir('tmp_models') + f'/{os.path.splitext(tflite_name)[0]}.tflite'
    tflite_model.save(tmp_tflite_path)

    if firmware_image_path is None:
        firmware_image_path = get_image(
            name=name,
            platform=platform,
            accelerator=accelerator,
            logger=logger
        )

    s37 = bincopy.BinFile()
    try:
        s37.add_srec_file(firmware_image_path)
    except Exception as e:
        raise Exception(f'Failed to process firmwage image, is it a valid .s37 file? Error details: {e}')

    mlmodel_section_address = None
    for segment in s37.segments:
        # Find the non-bootloader segment
        if segment.minimum_address < 0x0FE10000:
            # The ML model section's address is at the end of the FW image, 32-bit aligned
            mlmodel_section_address = ((segment.maximum_address + 3) // 4) * 4

    if not mlmodel_section_address:
        raise Exception('Failed to find valid segment in firmware .s37')

    s37.add_binary_file(tmp_tflite_path, mlmodel_section_address)

    # Generate an .s37 with the .tflite appended to the FW image
    tmp_s37_path = create_tempdir('tmp_firmware') + f'/{os.path.basename(firmware_image_path)}'
    with open(tmp_s37_path, 'w') as fp:
        fp.write(s37.as_srec())

    show_progress = is_command_active()
    if show_progress and hasattr(logger, 'verbose'):
        show_progress = logger.verbose

    # Program the generated .s37
    # and halt the CPU after programming
    logger.info(f'Programming FW image: {name} and ML model: {tflite_name} to device ...')
    commander.program_flash(
        tmp_s37_path, 
        platform=platform,
        show_progress=show_progress,
        halt=halt,
    )

    os.remove(tmp_s37_path)
    os.remove(tmp_tflite_path)


def get_url_key(name:str, platform:str, accelerator: str) -> str:
    name = name.lower()
    platform = platform.lower()
    accelerator = accelerator or 'none'
    accelerator = accelerator.lower()
    return f'{name}-{platform}-{accelerator}'


def get_image_extension(platform:str) -> str:
    """Return the image extension used by the given platform"""
    if platform == 'windows':
        return '.exe'
    elif platform in ('linux', 'osx'):
        return ''
    else:
        return '.s37'