import logging

from mltk import MLTK_ROOT_DIR
from mltk.utils.cmake import build_mltk_target
from mltk.utils.path import remove_directory 


def build_mvp_wrapper(
    clean:bool=True, 
    verbose:bool=False,
    logger:logging.Logger=None,
    use_user_options=False,
    debug:bool=False,
):  
    """Build the MVP kernels + simulator Python wrapper for the current OS/Python environment"""
    logger = logger or logging.getLogger()

    build_dir = f'{MLTK_ROOT_DIR}/build/_mvp_wrap'
    build_mltk_target(
        target='mltk_mvp_wrapper',
        build_dir=build_dir,
        source_dir=MLTK_ROOT_DIR,
        clean=clean,
        verbose=verbose,
        debug=debug,
        logger=logger,
        use_user_options=use_user_options,
    )

    if clean:
        remove_directory(build_dir)