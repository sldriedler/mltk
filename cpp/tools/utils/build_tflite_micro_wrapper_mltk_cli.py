
import logging
import typer

from mltk import cli, MLTK_ROOT_DIR
from mltk.utils.cmake import build_mltk_target


@cli.build_cli.command('tflite_micro_wrapper')
def build_tflite_micro_wrapper_command(
    verbose: bool = typer.Option(False, '--verbose', '-v', 
        help='Enable verbose console logs'
    ),
    clean: bool = typer.Option(True, 
        help='Clean the build directory before building'
    ),
    use_user_options: bool = typer.Option(False, '--user', '-u',
        help='Use the <mltk>/user_options.cmake file while building the wrapper. If omitted then this file is IGNORED'
    ),
    use_new_quantization: bool = typer.Option(False, '--new-quantization', '-q', 
        help='This option is deprecated. The new quantization method is now always used',
        hidden=True,
    ),
    debug: bool = typer.Option(False, '--debug', '-d',
        help='Build debug version of tflite wrapper')
):
    """Build the Tensorflow-Lite Micro Python wrapper

    \b
    This builds the Tensorflow-Lite Micro Python wrapper:  
    https://github.com/siliconlabs/mltk/tree/master/cpp/tflite_micro_wrapper
    \b
    NOTE: The built wrapper library is copied to:
    https://github.com/siliconlabs/mltk/tree/master/mltk/core/tflite_micro

    """

    logger = cli.get_logger(verbose=verbose)
    if use_new_quantization:
        logger.warning('--new-quantization is deprecated as the new quantization method is now always enabled')

    try:
        build_tflite_micro_wrapper(
            logger=logger,
            clean=clean,
            verbose=verbose,
            use_user_options=use_user_options,
            debug=debug
        )
    except Exception as e:
        cli.handle_exception('Failed to build tflite_micro_wrapper', e)

    logger.info('Done')


def build_tflite_micro_wrapper(
    clean:bool=False, 
    verbose:bool=True,
    logger:logging.Logger=None,
    use_user_options=False,
    debug:bool=False,
):  
    """Build the TF-Lite Micro Python wrapper for the current OS/Python environment"""
    logger = logger or logging.getLogger()

    build_mltk_target(
        target='mltk_tflite_micro_wrapper',
        build_subdir='tflm_wrap',
        source_dir=MLTK_ROOT_DIR,
        clean=clean,
        verbose=verbose,
        debug=debug,
        logger=logger,
        use_user_options=use_user_options,
    )
