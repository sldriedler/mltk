from typing import List, Union
import json
from mltk.utils import gpu
from mltk.utils.python import prepend_exception_msg
from .model import (
    load_mltk_model,
    load_tflite_or_keras_model,
    KerasModel,
    MltkModel,
    MltkModelEvent,
    EvaluateMixin,
    TrainMixin,
    DatasetMixin,
    EvaluateAutoEncoderMixin,
    EvaluateClassifierMixin
)
from .utils import get_mltk_logger
from .summarize_model import summarize_model
 # pylint: disable=unused-import
from .evaluation_results import EvaluationResults
from .evaluate_classifier import evaluate_classifier, ClassifierEvaluationResults
from .evaluate_autoencoder import evaluate_autoencoder, AutoEncoderEvaluationResults


def evaluate_model(
    model: Union[MltkModel, str],
    tflite:bool=False,
    weights:str=None,
    max_samples_per_class:int=-1,
    classes:List[str]=None,
    dump: bool=False,
    show: bool=False,
    verbose: bool=None,
    callbacks:List=None,
    update_archive:bool=True,
    test:bool=False,
    post_process:bool=False
) -> EvaluationResults:
    """Evaluate a trained model

    This internally calls:

    * :py:func:`mltk.core.evaluate_classifier`
    * :py:func:`mltk.core.evaluate_autoencoder`

    based on the given :py:class:`mltk.core.MltkModel` instance.

    .. seealso::
       * `Model Evaluation Guide <https://siliconlabs.github.io/mltk/docs/guides/model_evaluation.html>`_
       * `Model Evaluation API Examples <https://siliconlabs.github.io/mltk/mltk/examples/evaluate_model.html>`_


    Args:
        model: :py:class:`mltk.core.MltkModel` instance, name of MLTK model, path to
            model archive ``.mltk.zip`` or model specification script ``.py``
        tflite: If True, evaluate the ``.tflite`` (i.e. quantized) model file.
            If False, evaluate the Keras``.h5`` model (i.e. float)
        weights: Optional, load weights from previous training session.
            May be one of the following:

            * If option omitted then evaluate using output .h5 or .tflite from training
            * Absolute path to a generated weights .h5 file generated by Keras during training
            * The keyword ``best``; find the best weights in <model log dir>/train/weights
            * Filename of .h5 in <model log dir>/train/weights

            Note: This option may only be used if the "--tflite" option is *not* used
        max_samples_per_class: By default, all validation samples are used.
            This option places an upper limit on the number of samples per class that are used for evaluation
        classes: If evaluating a model with the :py:class:`mltk.core.EvaluateAutoEncoderMixin`,
            then this should be a comma-seperated list of classes in the dataset.
            The first element should be considered the "normal" class,
            every other class is considered abnormal and compared independently.
            If not provided, then the classes default to: [normal, abnormal]
        dump: If evaluating a model with the :py:class:`mltk.core.EvaluateAutoEncoderMixin`, then, for each sample,
            an image will be generated comparing the sample to the decoded sample
        show: Display the generated performance diagrams
        verbose: Enable verbose console logs
        callbacks: List of Keras callbacks to use for evaluation
        update_archive: Update the model archive with the evaluation results
        test: Optional, load the model in "test mode" if true.
        post_process: This allows for post-processing the evaluation results (e.g. uploading to a cloud) if supported by the given MltkModel

    Returns:
        Dictionary of evaluation results
    """

    if isinstance(model, MltkModel):
        mltk_model = model
        if test:
            mltk_model.enable_test_mode()

    elif isinstance(model, str):
        if model.endswith(('.tflite', '.h5')):
            raise ValueError(
                'Must provide name of MLTK model, '
                'path to model archive (.mltk.zip) or model specification script(.py)'
            )
        mltk_model = load_mltk_model(model, test=test)
    else:
        raise ValueError(
            'Must provide MltkModel instance, name of MLTK model, path to '
            'model archive (.mltk.zip) or model specification script(.py)'
        )

    mltk_model.trigger_event(
        MltkModelEvent.EVALUATE_STARTUP,
        tflite=tflite,
        max_samples_per_class=max_samples_per_class,
        post_process=post_process
    )

    # If a custom function was provided,
    # then be sure to use that instead of the default function that comes with
    # EvaluateAutoEncoderMixin or EvaluateClassifierMixin
    eval_custom_function = getattr(mltk_model, 'eval_custom_function', None)


    if eval_custom_function is None and isinstance(mltk_model, EvaluateAutoEncoderMixin):
        results = evaluate_autoencoder(
            mltk_model,
            tflite=tflite,
            weights=weights,
            max_samples_per_class=max_samples_per_class,
            classes=classes,
            dump=dump,
            show=show,
            verbose=verbose,
            callbacks=callbacks,
            update_archive=update_archive
        )

    elif eval_custom_function is None and isinstance(mltk_model, EvaluateClassifierMixin):
        results = evaluate_classifier(
            mltk_model,
            tflite=tflite,
            weights=weights,
            max_samples_per_class=max_samples_per_class,
            classes=classes,
            show=show,
            verbose=verbose,
            callbacks=callbacks,
            update_archive=update_archive
        )

    elif isinstance(mltk_model, EvaluateMixin):
        results = evaluate_custom(
            mltk_model,
            tflite=tflite,
            weights=weights,
            verbose=verbose,
            callbacks=callbacks,
            show=show,
            update_archive=update_archive,
            max_samples_per_class=max_samples_per_class,
        )

    else:
        raise RuntimeError('MltkModel instance must inherit EvaluateMixin, EvaluateClassifierMixin or EvaluateAutoEncoderMixin')

    mltk_model.trigger_event(
        MltkModelEvent.EVALUATE_SHUTDOWN,
        results=results,
    )


    return results


def evaluate_custom(
    mltk_model:MltkModel,
    tflite:bool=False,
    weights:str=None,
    callbacks:list=None,
    verbose:bool=False,
    show:bool=False,
    update_archive:bool=True,
    max_samples_per_class:int=-1
) -> EvaluationResults:
    """Evaluate a trained model based on the model's implementation

    Args:
        mltk_model: MltkModel instance
        tflite: If true then evalute the .tflite (i.e. quantized) model, otherwise evaluate the keras model
        weights: Optional weights to load before evaluating (only valid for a keras model)
        verbose: Enable verbose log messages
        callbacks: Optional callbacks to invoke while evaluating
        update_archive: Update the model archive with the eval results
        max_samples_per_class: Maximum number of samples per class to evaluate. This is useful for large datasets

    Returns:
        Dictionary containing evaluation results
    """


    if not isinstance(mltk_model, TrainMixin):
        raise RuntimeError('MltkModel must inherit TrainMixin')
    if not isinstance(mltk_model, EvaluateMixin):
        raise RuntimeError('MltkModel must inherit EvaluateClassifierMixin')
    if not isinstance(mltk_model, DatasetMixin):
        raise RuntimeError('MltkModel must inherit a DatasetMixin')

    subdir = 'eval/tflite' if tflite else 'eval/h5'
    eval_dir = mltk_model.create_log_dir(subdir, delete_existing=True)
    logger = mltk_model.create_logger('eval', parent=get_mltk_logger())

    if update_archive:
        update_archive = mltk_model.check_archive_file_is_writable()
    gpu.initialize(logger=logger)

    try:
        mltk_model.load_dataset(
            subset='evaluation',
            test=mltk_model.test_mode_enabled,
            max_samples_per_class=max_samples_per_class,
        )
    except Exception as e:
        prepend_exception_msg(e, 'Failed to load model evaluation dataset')
        raise

    # Build the MLTK model's corresponding as a Keras model or .tflite
    try:
        built_model = load_tflite_or_keras_model(
            mltk_model,
            model_type='tflite' if tflite else 'h5',
            weights=weights
        )
    except Exception as e:
        prepend_exception_msg(e, 'Failed to build model')
        raise

    try:
        summary = summarize_model(
            mltk_model,
            built_model=built_model
        )
        logger.info(summary)
    except Exception as e:
        logger.debug(f'Failed to generate model summary, err: {e}', exc_info=e)
        logger.warning(f'Failed to generate model summary, err: {e}')

    logger.info(mltk_model.summarize_dataset())


    eval_custom_function = getattr(mltk_model, 'eval_custom_function', None)

    try:
        if eval_custom_function is not None:
            try:
                results = eval_custom_function(
                    mltk_model,
                    built_model=built_model,
                    eval_dir=eval_dir,
                    show=show,
                    logger=logger
                )
            except Exception as e:
                prepend_exception_msg(e, 'Failed to evaluate using custom callback')
                raise

        elif isinstance(built_model, KerasModel):
            validation_data = mltk_model.validation_data
            if validation_data is None:
                validation_data = mltk_model.x

            eval_loss, eval_accuracy = built_model.evaluate(
                x=validation_data,
                y=mltk_model.y,
                batch_size=mltk_model.batch_size,
                verbose=1 if verbose else 0,
                callbacks=callbacks,
                steps=mltk_model.eval_steps_per_epoch
            )
            results = EvaluationResults(
                name=mltk_model.name
            )
            results['overall_loss'] = eval_loss
            results['overall_accuracy'] = eval_accuracy

        else:
            raise RuntimeError('Must specify my_model.eval_custom_function to evaluate a .tflite model')

    finally:
        mltk_model.unload_dataset()

    eval_results_path = f'{eval_dir}/eval-results.json'
    with open(eval_results_path, 'w') as f:
        json.dump(results, f)
    logger.debug(f'Generated {eval_results_path}')

    summary_path = f'{eval_dir}/summary.txt'
    with open(summary_path, 'w') as f:
        f.write(results.generate_summary())
    logger.debug(f'Generated {summary_path}')

    try:
        results.generate_plots(
            logger=logger,
            output_dir=eval_dir,
            show=show
        )
    except NotImplementedError:
        pass
    except Exception as e:
        logger.warning(f'Failed to generate evaluation plots', exc_info=e)

    if update_archive:
        try:
            logger.info(f'Updating {mltk_model.archive_path}')
            mltk_model.add_archive_dir(subdir)
        except Exception as e:
            logger.warning(f'Failed to add eval results to model archive, err: {e}', exc_info=e)

    return results