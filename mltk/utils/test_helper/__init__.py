import os
import sys
import threading
from mltk.utils.shell_cmd import run_shell_cmd
from mltk.core.utils import get_mltk_logger
from mltk.utils.logger import make_filelike

logger = get_mltk_logger()

_lock = threading.Lock()


def run_mltk_command(*args, update_model_path=False) -> str:
    env = os.environ.copy()

    python_bin_dir = os.path.dirname(os.path.abspath(sys.executable))
    mltk_exe_path = os.path.join(python_bin_dir, 'mltk')

    env['MLTK_UNIT_TEST'] = '1'
    cmd = [mltk_exe_path]
    cmd.extend(args)
    cmd_str = ' '.join([str(x) for x in cmd])
    logger.info(f'Running {cmd_str}')
    make_filelike(logger)

    with _lock:
        if update_model_path:
            env['MLTK_MODEL_PATHS'] = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
        retcode, retmsg = run_shell_cmd(cmd, outfile=logger, env=env)
        if retcode not in (0, 2):
            raise RuntimeError(f'Command failed (err code={retcode}): {cmd_str}\n{retmsg}')
    return retmsg
        

def generate_run_model_params(
    train=True,
    evaluate=True,
    profile=True,
    summarize=True,
    quantize=True,
    view=True,
    build=None,
    tflite=None
):
    names = ['op', 'tflite', 'build']
    params = []

    if train:
        params.append(('train', False, False))

    if evaluate:
        params.append(('evaluate', False, False))

    if profile:
        if build is None:
            params.append(('profile', False, False))
            params.append(('profile', False, True))
        else:
            params.append(('profile', False, build))
        
    if summarize:
        if build is None and tflite is None:
            params.append(('summarize', False, False))
            params.append(('summarize', False, True))
            params.append(('summarize', True, False))
            params.append(('summarize', True, True))
        elif build is not None and tflite is None: 
            params.append(('summarize', False, build))
            params.append(('summarize', True, build))
        elif build is None and tflite is not None: 
            params.append(('summarize', tflite, False))
            params.append(('summarize', tflite, True))
        else:
            params.append(('summarize', tflite, build))
        
    if quantize:
        params.append(('quantize', False, False))

    if view:
        if build is None and tflite is None:
            params.append(('view', False, False))
            params.append(('view', False, True))
            params.append(('view', True, False))
            params.append(('view', True, True))
        elif build is not None and tflite is None: 
            params.append(('view', False, build))
            params.append(('view', True, build))
        elif build is None and tflite is not None: 
            params.append(('view', tflite, False))
            params.append(('view', tflite, True))
        else:
            params.append(('view', tflite, build))

    return names, params


def run_model_operation(
    name_or_archive:str, 
    op:str,
    tflite=False,
    build=False
):
    logger.info(f'Testing {name_or_archive}, op={op}, tflite={tflite}, build={build}')

    if op == 'train':
        run_mltk_command('train', name_or_archive, '--clean', '--verbose')
    
    elif op == 'evaluate':
        run_mltk_command('evaluate', name_or_archive, '--verbose')
    
    elif op == 'profile':
        if build:
            name_no_test = name_or_archive.replace('-test', '')
            run_mltk_command('profile', name_no_test, '--build', '--verbose')
        else:
            run_mltk_command('profile', name_or_archive, '--verbose')
        
    elif op == 'summarize':
        if build:
            name_no_test = name_or_archive.replace('-test', '')
            if tflite:
                run_mltk_command('summarize', name_no_test, '--tflite', '--build', '--verbose')
            else:
                run_mltk_command('summarize', name_no_test, '--build', '--verbose')
        else:
            if tflite:
                run_mltk_command('summarize', name_or_archive, '--tflite', '--verbose')
            else:
                run_mltk_command('summarize', name_or_archive, '--verbose')

    elif op == 'quantize':
        run_mltk_command('quantize', name_or_archive, '--verbose')

    elif op == 'view':
        if build:
            name_no_test = name_or_archive.replace('-test', '')
            if tflite:
                run_mltk_command('view', name_no_test, '--tflite', '--build', '--verbose')
            else:
                run_mltk_command('view', name_no_test, '--build', '--verbose')
        else:           
            if tflite:
                run_mltk_command('view', name_or_archive, '--tflite', '--verbose')
            else:
                run_mltk_command('view', name_or_archive, '--verbose')
