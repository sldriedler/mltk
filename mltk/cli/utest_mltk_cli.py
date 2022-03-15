import sys
import os
import typer
import pytest

from mltk import cli


@cli.root_cli.command('utest')
def utest_command(
    test_type: str = typer.Argument(None, 
        help='''\b
Comma separated list of unit test types, options are:
- all - Run all the tests, default if omitted
- cli - Run CLI tests
- api - Run API tests
- model - Run reference model tests
'''
    ),
    test_arg: str = typer.Argument(None, 
        help='Argument for specific test(s) to run. Refer to the pytests -k option for more details: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name'
    ),
    verbose: bool = typer.Option(False, '--verbose', '-v', 
        help='Enable verbose console logs'
    ),
    list_only: bool = typer.Option(False, '--list', '-l', 
        help='Only list the available unit tests'
    )
):
    """Run the all unit tests"""

    # Import all required packages here instead of at top
    # to help improve the CLI's responsiveness
    from mltk import MLTK_DIR, MLTK_ROOT_DIR
    from mltk.utils.python import as_list
    from mltk.utils.path import create_user_dir
    from mltk.utils.path import create_tempdir, clean_directory
    from mltk.utils.logger import get_logger, make_filelike

    all_types = {'all', 'cli', 'api', 'model'}
    test_type = test_type or 'all'
    test_type = set(test_type.split(','))

    if not test_type.issubset(all_types):
        cli.abort(msg=f'Unsupported test type: {",".join(test_type)}. Supported types are: {",".join(all_types)}')


    test_dirs = []
    if test_type & {'all', 'cli'}:
        test_dirs.append('cli/tests')

    if test_type & {'all', 'api'}:
        test_dirs.append('core/tflite_micro/tests')
        test_dirs.append('core/tflite_model/tests')
        test_dirs.append('core/tflite_model_parameters/tests')
        test_dirs.append('core/preprocess/audio/audio_feature_generator/tests')

    if test_type & {'all', 'model'}:
        test_dirs.append('models/tests')

 

    test_dirs = as_list(test_dirs)
    log_dir = create_user_dir('pytest_results')
    log_path = f'{log_dir}/pytest_results.txt'
    logger = get_logger(
        'utest', 
        level='DEBUG', 
        console=True, 
        log_file=log_path
    )

    utest_cache_dir = create_tempdir('utest_cache')
    clean_directory(utest_cache_dir)
    os.environ['MLTK_CACHE_DIR'] = utest_cache_dir
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1' # Disable the GPU as well
    cli.print_info(f'Setting MLTK_CACHE_DIR="{os.environ["MLTK_CACHE_DIR"]}"')
    cli.print_info('Setting CUDA_VISIBLE_DEVICES=-1')

    make_filelike(logger)
    logger.set_terminator('')
    logger.verbose = True

    cmd = []
    cmd.append(f'--rootdir={MLTK_ROOT_DIR}')
    cmd.append(f'--html-report={log_dir}/report.html')
    cmd.append('--color=yes')
    cmd.extend(['-o', 'log_cli=true'])
    if verbose:
        cmd.append('-v')
        cmd.append('--log-cli-level=DEBUG')
    cmd.append('--show-capture=all')
    cmd.extend(['-W', 'ignore::DeprecationWarning'])
    if list_only:
        cmd.append('--collect-only')
    if test_arg is not None:
        cmd.extend(['-k', test_arg])

    for d in test_dirs:
        cmd.append(f'{MLTK_DIR}/{d}')
    

    cli.print_info('Executing: pytest ' + " ".join(cmd))
    retcode = pytest.main(cmd)
    
    cli.print_info(f'\n\nFor more details, see: {log_path}')
    cli.abort(code=retcode)