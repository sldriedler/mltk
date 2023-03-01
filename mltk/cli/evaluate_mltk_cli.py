
import typer

from mltk import cli


@cli.root_cli.command('evaluate')
def evaluate_model_command(
    model: str = typer.Argument(...,
        help='''Name of previously trained MLTK model or path to trained model's archive (.mltk.zip)''',
        metavar='<model>'
    ),
    tflite: bool = typer.Option(False, '--tflite',
        help='''\b
Evaluate the .tflite (i.e. quantized) model file.
If omitted, evaluate the Keras .h5 model (i.e. float)''',
    ),
    weights: str = typer.Option(None, '--weights', '-w',
        help='''\b
Optional, load weights from previous training session.
May be one of the following:
- If option omitted then evaluate using output .h5 or .tflite from training
- Absolute path to a generated weights .h5 file generated by Keras during training
- The keyword `best`; find the best weights in <model log dir>/train/weights
- Filename of .h5 in <model log dir>/train/weights
Note: This option may only be used if the "--tflite" option is *not* used
''',
    metavar='<weights>'
    ),
    classes: str = typer.Option(None,
        help='''\b
If evaluating a model with the EvaluateAutoEncoderMixin mixin,
then this should be a comma-seperated list of classes in the dataset.
The first element should be considered the "normal" class,
every other class is considered abnormal and compared independently.
If not provided, then the classes default to: [normal, abnormal]''',
        metavar='<class-list>'
    ),
    max_samples_per_class: int = typer.Option(-1, '--count', '-c',
        help='''\b
By default, all validation samples are used.
This option places an upper limit on the number of samples per class that are used for evaluation''',
        metavar='<value>'
    ),
    dump: bool = typer.Option(False,
        help='If evaluating a model with the EvaluateAutoEncoderMixin mixin, then, for each sample, ' \
            'an image will be generated comparing the sample to the decoded sample'
    ),
    show: bool = typer.Option(False,
        help='Display the generated performance diagrams'
    ),
    verbose: bool = typer.Option(False, '--verbose', '-v',
        help='Enable verbose console logs'
    ),
    update_archive: bool = typer.Option(True,
        help='Update the model archive with the evaluation results'
    ),
    test: bool = typer.Option(False,
        help='Use the model created by the test training. This does the same thing as: mltk evaluate my_model-test'
    ),
    post_process: bool = typer.Option(False, '--post',
        help='This allows for post-processing the evaluation results (e.g. uploading to a cloud) if supported by the given MltkModel'
    )
):
    """Evaluate a trained ML model

    This passes validation samples through a trained MLTK model and generates a model performance summary.
    
    \b
    For more details see:
    https://siliconlabs.github.io/mltk/docs/guides/model_evaluation
    \b
    ----------
     Examples
    ----------
    \b
    # Evaluate the .h5 (i.e. float32) model
    mltk evaluate audio_example1
    \b
    # Evaluate the .h5 (i.e. float32) using model archive
    mltk evaluate ~/workspace/my_model.mltk.zip
    \b
    # Evaluate the .tflite (i.e. quantized) model
    # and limit the max samples per class to 100
    mltk evaluate audio_example1 --tflite --count 100
    \b
    # Evaluate the .tflite (i.e. quantized) auto encoder model
    # and dump the input/output images
    mltk evaluate fully_connected_autoencoder --tflite --dump
    \b
    Note: All log files are generated in the <model log dir>/eval directory.
    It a MLTK model is provided, the model's archive is updated with the evaluation results.
    """

    # Import all required packages here instead of at top
    # to help improve the CLI's responsiveness
    from mltk.core import (evaluate_model, load_mltk_model)


    logger = cli.get_logger(verbose=verbose)

    if tflite and max_samples_per_class == -1:
        logger.warning(
            'Hint: It is recommended to use the --count option '
            'with the --tflite option as running quantized models on the PC can be slow'
        )


    if classes:
        classes = classes.split(',')

    # Find the MLTK Model file
    try:
        mltk_model = load_mltk_model(
            model,
            test=test,
            print_not_found_err=True
        )
    except Exception as e:
        cli.handle_exception('Failed to load model', e)


    # Find the MLTK Model file
    try:
        results = evaluate_model(
            mltk_model,
            tflite=tflite,
            weights=weights,
            max_samples_per_class=max_samples_per_class,
            classes=classes,
            dump=dump,
            show=show,
            verbose=True,
            update_archive=update_archive,
            post_process=post_process
       )
    except Exception as e:
        cli.handle_exception('Failed to evaluate model', e)


    if not show:
        cli.print_info('Hint: Add --show to view the result diagrams')

    cli.print_info(results.generate_summary())
    cli.print_info(f'See {mltk_model.archive_path} for more details')