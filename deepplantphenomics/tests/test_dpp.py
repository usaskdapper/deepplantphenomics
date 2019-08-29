import pytest
import numpy as np
import os.path
import tensorflow as tf
import deepplantphenomics as dpp
from deepplantphenomics.tests.mock_dpp_model import MockDPPModel

# public setters and adders, mostly testing for type and value errors
@pytest.fixture(scope="module")
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture()
def model():
    model = MockDPPModel()
    model.set_image_dimensions(1, 1, 1)
    return model


def test_set_number_of_threads(model):
    with pytest.raises(TypeError):
        model.set_number_of_threads(5.0)
    with pytest.raises(ValueError):
        model.set_number_of_threads(-1)


def test_set_processed_images_dir(model):
    with pytest.raises(TypeError):
        model.set_processed_images_dir(5)


def test_set_batch_size(model):
    with pytest.raises(TypeError):
        model.set_batch_size(5.0)
    with pytest.raises(ValueError):
        model.set_batch_size(-1)


def test_set_num_regression_outputs():
    model = dpp.RegressionModel()

    with pytest.raises(TypeError):
        model.set_num_regression_outputs(5.0)
    with pytest.raises(ValueError):
        model.set_num_regression_outputs(-1)


def test_set_density_map_sigma():
    model = dpp.HeatmapObjectCountingModel()
    assert model._density_sigma == 5

    with pytest.raises(TypeError):
        model.set_density_map_sigma('4')
    model.set_density_map_sigma(2.0)
    assert model._density_sigma == 2.0


def test_set_maximum_training_epochs(model):
    with pytest.raises(TypeError):
        model.set_maximum_training_epochs(5.0)
    with pytest.raises(ValueError):
        model.set_maximum_training_epochs(-1)


def test_set_learning_rate(model):
    # Give the type checking a workout
    with pytest.raises(TypeError):
        model.set_learning_rate("5")
    with pytest.raises(ValueError):
        model.set_learning_rate(-0.001)

    # Ensure a good value sets the rate properly
    model.set_learning_rate(0.01)
    assert model._learning_rate == 0.01

    # Ensure that the internal learning rate setter doesn't touch it (due to no decay settings)
    model._set_learning_rate()
    assert model._learning_rate == 0.01


def test_set_crop_or_pad_images(model):
    with pytest.raises(TypeError):
        model.set_crop_or_pad_images("True")


def test_set_resize_images(model):
    with pytest.raises(TypeError):
        model.set_resize_images("True")


def test_set_augmentation_flip_horizontal():
    model1 = dpp.RegressionModel()
    model2 = dpp.SemanticSegmentationModel()

    with pytest.raises(TypeError):
        model1.set_augmentation_flip_horizontal("True")
    with pytest.raises(RuntimeError):
        model2.set_augmentation_flip_horizontal(True)
    model1.set_augmentation_flip_horizontal(True)


def test_set_augmentation_flip_vertical():
    model1 = dpp.RegressionModel()
    model2 = dpp.SemanticSegmentationModel()

    with pytest.raises(TypeError):
        model1.set_augmentation_flip_vertical("True")
    with pytest.raises(RuntimeError):
        model2.set_augmentation_flip_vertical(True)
    model1.set_augmentation_flip_vertical(True)


def test_set_augmentation_crop():
    model1 = dpp.RegressionModel()
    model2 = dpp.SemanticSegmentationModel()

    with pytest.raises(TypeError):
        model1.set_augmentation_crop("True", 0.5)
    with pytest.raises(TypeError):
        model1.set_augmentation_crop(True, "5")
    with pytest.raises(ValueError):
        model1.set_augmentation_crop(False, -1.0)
    with pytest.raises(RuntimeError):
        model2.set_augmentation_crop(True)
    model1.set_augmentation_crop(True)


def test_set_augmentation_brightness_and_contrast():
    model1 = dpp.RegressionModel()
    model2 = MockDPPModel()
    model2._supported_augmentations = []

    with pytest.raises(TypeError):
        model1.set_augmentation_crop("True")
    with pytest.raises(RuntimeError):
        model2.set_augmentation_brightness_and_contrast(True)
    model1.set_augmentation_brightness_and_contrast(True)


def test_set_augmentation_rotation():
    model1 = dpp.RegressionModel()
    model2 = dpp.SemanticSegmentationModel()

    # Check the type-checking
    with pytest.raises(TypeError):
        model1.set_augmentation_rotation("True")
    with pytest.raises(TypeError):
        model1.set_augmentation_rotation(True, crop_borders="False")
    with pytest.raises(RuntimeError):
        model2.set_augmentation_rotation(True)

    # Check that rotation augmentation can be turned on the simple way
    model1.set_augmentation_rotation(True)
    assert model1._augmentation_rotate is True
    assert model1._rotate_crop_borders is False

    # Check that it can be turned on with a border cropping setting
    model1.set_augmentation_rotation(False, crop_borders=True)
    assert model1._augmentation_rotate is False
    assert model1._rotate_crop_borders is True


def test_set_regularization_coefficient(model):
    with pytest.raises(TypeError):
        model.set_regularization_coefficient("5")
    with pytest.raises(ValueError):
        model.set_regularization_coefficient(-0.001)


def test_set_learning_rate_decay(model):
    # Give the type checking a workout
    with pytest.raises(TypeError):
        model.set_learning_rate_decay("5", 1)
    with pytest.raises(ValueError):
        model.set_learning_rate_decay(-0.001, 1)
    with pytest.raises(TypeError):
        model.set_learning_rate_decay(0.5, 5.0)
    with pytest.raises(ValueError):
        model.set_learning_rate_decay(0.5, -1)

    # Ensure that a good set of inputs sets model parameters properly
    model.set_learning_rate_decay(0.01, 100)
    assert model._lr_decay_factor == 0.01
    assert model._epochs_per_decay == 100
    assert model._lr_decay_epochs is None

    # Ensure that the internal learning rate setter handles decay properly
    model._total_training_samples = 100
    model._test_split = 0.20
    model._learning_rate = 0.1
    model._global_epoch = 0
    model._set_learning_rate()
    assert model._lr_decay_epochs == 8000
    assert isinstance(model._learning_rate, tf.Tensor)
    with tf.Session() as sess:
        assert sess.run(model._learning_rate) == pytest.approx(0.1)


def test_set_optimizer(model):
    with pytest.raises(TypeError):
        model.set_optimizer(5)
    with pytest.raises(ValueError):
        model.set_optimizer('Nico')
    model.set_optimizer('adam')
    assert model._optimizer == 'adam'
    model.set_optimizer('Adam')
    assert model._optimizer == 'adam'
    model.set_optimizer('ADAM')
    assert model._optimizer == 'adam'
    model.set_optimizer('SGD')
    assert model._optimizer == 'sgd'
    model.set_optimizer('sgd')
    assert model._optimizer == 'sgd'
    model.set_optimizer('sGd')
    assert model._optimizer == 'sgd'


def test_set_weight_initializer(model):
    with pytest.raises(TypeError):
        model.set_weight_initializer(5)
    with pytest.raises(ValueError):
        model.set_weight_initializer('Nico')
    model.set_weight_initializer('normal')
    assert model._weight_initializer == 'normal'
    model.set_weight_initializer('Normal')
    assert model._weight_initializer == 'normal'
    model.set_weight_initializer('NORMAL')
    assert model._weight_initializer == 'normal'


def test_set_image_dimensions(model):
    with pytest.raises(TypeError):
        model.set_image_dimensions(1.0, 1, 1)
    with pytest.raises(ValueError):
        model.set_image_dimensions(-1, 1, 1)
    with pytest.raises(TypeError):
        model.set_image_dimensions(1, 1.0, 1)
    with pytest.raises(ValueError):
        model.set_image_dimensions(1, -1, 1)
    with pytest.raises(TypeError):
        model.set_image_dimensions(1, 1, 1.0)
    with pytest.raises(ValueError):
        model.set_image_dimensions(1, 1, -1)


def test_set_original_image_dimensions(model):
    with pytest.raises(TypeError):
        model.set_original_image_dimensions(1.0, 1)
    with pytest.raises(ValueError):
        model.set_original_image_dimensions(-1, 1)
    with pytest.raises(TypeError):
        model.set_original_image_dimensions(1, 1.0)
    with pytest.raises(ValueError):
        model.set_original_image_dimensions(1, -1)


def test_set_patch_size(model):
    with pytest.raises(TypeError):
        model.set_patch_size(1.0, 1)
    with pytest.raises(ValueError):
        model.set_patch_size(-1, 1)
    with pytest.raises(TypeError):
        model.set_patch_size(1, 1.0)
    with pytest.raises(ValueError):
        model.set_patch_size(1, -1)


@pytest.mark.parametrize("model,bad_loss,good_loss",
                         [(dpp.ClassificationModel(), 'l2', 'softmax cross entropy'),
                          (dpp.RegressionModel(), 'softmax cross entropy', 'l2'),
                          (dpp.SemanticSegmentationModel(), 'l2', 'sigmoid cross entropy'),
                          (dpp.ObjectDetectionModel(), 'l2', 'yolo'),
                          (dpp.CountCeptionModel(), 'l2', 'l1'),
                          (dpp.HeatmapObjectCountingModel(), 'l1', 'sigmoid cross entropy')])
def test_set_loss_function(model, bad_loss, good_loss):
    with pytest.raises(TypeError):
        model.set_loss_function(0)
    with pytest.raises(ValueError):
        model.set_loss_function(bad_loss)
    model.set_loss_function(good_loss)


def test_set_yolo_parameters():
    model = dpp.ObjectDetectionModel()
    with pytest.raises(RuntimeError):
        model.set_yolo_parameters()
    model.set_image_dimensions(448, 448, 3)
    model.set_yolo_parameters()

    with pytest.raises(TypeError):
        model.set_yolo_parameters(True, ['plant', 'knat'], [(100, 30), (200, 10), (50, 145)])
    with pytest.raises(TypeError):
        model.set_yolo_parameters(13, ['plant', 'knat'], [(100, 30), (200, 10), (50, 145)])
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13], ['plant', 'knat'], [(100, 30), (200, 10), (50, 145)])
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13, 13], 'plant', [(100, 30), (200, 10), (50, 145)])
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13, 13], ['plant', 2], [(100, 30), (200, 10), (50, 145)])
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13, 13], ['plant', 'knat'], 100)
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13, 13], ['plant', 'knat'], [(100, 30), (200, 10), 50])
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13, 13], ['plant', 'knat'], [(100, 30), (200, 10), (145,)])
    with pytest.raises(TypeError):
        model.set_yolo_parameters([13, 13], ['plant', 'knat'], [(100, 30), (200, 10), (145, 'a')])
    model.set_yolo_parameters([13, 13], ['plant', 'knat'], [(100, 30), (200, 10), (50, 145)])


# adding layers may require some more indepth testing
def test_add_input_layer(model):
    model.set_batch_size(1)
    model.set_image_dimensions(1, 1, 1)
    model.add_input_layer()
    assert isinstance(model._last_layer(), dpp.layers.inputLayer)
    with pytest.raises(RuntimeError):
        model.add_input_layer()


# need to come back to this one
# need to add exceptions to real function, and set up the layer for the test better
# def test_add_moderation_layer(model):
#     mf = np.array([[0, 1, 2]])
#     model.add_moderation_features(mf)
#     model.add_moderation_layer()
#     assert isintance(model._DPPModel__last_layer(), layers.moderationLayer)
#     model.add_moderation_layer()
#     assert isinstance(model._DPPModel__last_layer(), layers.moderationLayer)


def test_add_convolutional_layer(model):
    with pytest.raises(RuntimeError):
        model.add_convolutional_layer([1, 2.0, 3, 4], 1, 'relu')
    model.add_input_layer()
    with pytest.raises(TypeError):
        model.add_convolutional_layer([1, 2.0, 3, 4], 1, 'relu')
    with pytest.raises(TypeError):
        model.add_convolutional_layer([1, 2], 1, 'relu')
    with pytest.raises(TypeError):
        model.add_convolutional_layer([1, 2, 3, 4], 1.0, 'relu')
    with pytest.raises(ValueError):
        model.add_convolutional_layer([1, 2, 3, 4], -1, 'relu')
    with pytest.raises(TypeError):
        model.add_convolutional_layer([1, 2, 3, 4], 1, 555)
    with pytest.raises(ValueError):
        model.add_convolutional_layer([1, 2, 3, 4], 1, 'Nico')
    model.add_convolutional_layer(np.array([1, 1, 1, 1]), 1, 'relu')
    assert isinstance(model._last_layer(), dpp.layers.convLayer)


def test_add_paral_conv_block(model):
    with pytest.raises(RuntimeError):
        model.add_paral_conv_block([1, 1, 1, 1], [1, 1, 1, 1])
    model.add_input_layer()
    with pytest.raises(TypeError):
        model.add_paral_conv_block([1, 1, 1, 1], [1, 2.0, 1, 1])
    with pytest.raises(TypeError):
        model.add_paral_conv_block([1, 1, 1, 1], [1, 1, 1])
    with pytest.raises(TypeError):
        model.add_paral_conv_block([1, 1, 1, 1], 1)
    model.add_paral_conv_block([1, 1, 1, 1], [1, 1, 1, 1])
    assert isinstance(model._last_layer(), dpp.layers.paralConvBlock)


def test_add_pooling_layer(model):
    with pytest.raises(RuntimeError):
        model.add_pooling_layer(1, 1, 'avg')
    model.add_input_layer()
    with pytest.raises(TypeError):
        model.add_pooling_layer(1.5, 1)
    with pytest.raises(ValueError):
        model.add_pooling_layer(-1, 1)
    with pytest.raises(TypeError):
        model.add_pooling_layer(1, 1.5)
    with pytest.raises(ValueError):
        model.add_pooling_layer(1, -1)
    with pytest.raises(TypeError):
        model.add_pooling_layer(1, 1, 5)
    with pytest.raises(ValueError):
        model.add_pooling_layer(1, 1, 'Nico')
    model.add_pooling_layer(1, 1, 'avg')
    assert isinstance(model._last_layer(), dpp.layers.poolingLayer)


@pytest.mark.parametrize("kernel_size,stride,output_size", [(2, 2, 3), (3, 3, 2), (2, 1, 5)])
def test_pooling_layer_output_size(model, kernel_size, stride, output_size):
    model.set_image_dimensions(5, 5, 1)
    model.add_input_layer()
    model.add_pooling_layer(kernel_size, stride)
    assert model._last_layer().output_size == [1, output_size, output_size, 1]


def test_add_normalization_layer(model):
    with pytest.raises(RuntimeError):
        model.add_normalization_layer()
    model.add_input_layer()
    model.add_normalization_layer()
    assert isinstance(model._last_layer(), dpp.layers.normLayer)


def test_add_dropout_layer(model):
    with pytest.raises(RuntimeError):
        model.add_dropout_layer(0.4)
    model.add_input_layer()
    with pytest.raises(TypeError):
        model.add_dropout_layer("0.5")
    with pytest.raises(ValueError):
        model.add_dropout_layer(1.5)
    model.add_dropout_layer(0.4)
    assert isinstance(model._last_layer(), dpp.layers.dropoutLayer)


def test_add_batch_norm_layer(model):
    with pytest.raises(RuntimeError):
        model.add_batch_norm_layer()
    model.add_input_layer()
    model.add_batch_norm_layer()
    assert isinstance(model._last_layer(), dpp.layers.batchNormLayer)


def test_add_fully_connected_layer(model):
    with pytest.raises(RuntimeError):
        model.add_fully_connected_layer(1, 'tanh', 0.3)
    model.add_input_layer()
    with pytest.raises(TypeError):
        model.add_fully_connected_layer(2.3, 'relu', 1.8)
    with pytest.raises(ValueError):
        model.add_fully_connected_layer(-3, 'relu', 1.8)
    with pytest.raises(TypeError):
        model.add_fully_connected_layer(2, 5, 1.8)
    with pytest.raises(ValueError):
        model.add_fully_connected_layer(3, 'Nico', 1.8)
    with pytest.raises(TypeError):
        model.add_fully_connected_layer(2, 'relu', "1.8")
    with pytest.raises(ValueError):
        model.add_fully_connected_layer(3, 'relu', -1.5)
    model.add_fully_connected_layer(1, 'tanh', 0.3)
    assert isinstance(model._last_layer(), dpp.layers.fullyConnectedLayer)


def test_add_output_layer():
    model1 = dpp.ClassificationModel()
    model2 = dpp.SemanticSegmentationModel()
    model3 = dpp.CountCeptionModel()
    model1.set_image_dimensions(5,5,3)
    model2.set_image_dimensions(5,5,3)

    with pytest.raises(RuntimeError):
        model1.add_output_layer(2.5, 3)
    model1.add_input_layer()
    model2.add_input_layer()
    model3.add_input_layer()
    with pytest.raises(TypeError):
        model1.add_output_layer("2")
    with pytest.raises(ValueError):
        model1.add_output_layer(-0.4)
    with pytest.raises(TypeError):
        model1.add_output_layer(2.0, 3.4)
    with pytest.raises(ValueError):
        model1.add_output_layer(2.0, -4)
    with pytest.raises(RuntimeError):
        model2.add_output_layer(output_size=3)  # Semantic segmentation needed for this runtime error to occur

    model1.add_output_layer(2.5, 3)
    assert isinstance(model1._last_layer(), dpp.layers.fullyConnectedLayer)
    with pytest.warns(Warning):
        model2.add_output_layer(regularization_coefficient=2.0)
    assert isinstance(model2._last_layer(), dpp.layers.convLayer)
    model3.add_output_layer()
    assert isinstance(model3._last_layer(), dpp.layers.inputLayer)


# having issue with not being able to create a new model, they all seem to inherit the fixture model
# used in previous test functions and thus can't properly add a new outputlayer for this test
# @pytest.fixture
# def model2():
#     model2 = dpp.DPPModel()
#     return model2
# def test_add_output_layer_2(model2): # semantic_segmentation problem type
#     model2.set_batch_size(1)
#     model2.set_image_dimensions(1, 1, 1)
#     model2.add_input_layer()
#     model2.set_problem_type('semantic_segmentation')
#     model2.add_output_layer(2.5)
#     assert isinstance(model2._DPPModel__last_layer(), layers.convLayer)


# more loading data tests!!!!
def test_load_dataset_from_directory_with_csv_labels(model, test_data_dir):
    im_path = os.path.join(test_data_dir, 'test_dir_csv_labels', '')
    label_path = os.path.join(test_data_dir, 'test_csv_labels.txt')
    with pytest.raises(TypeError):
        model.load_dataset_from_directory_with_csv_labels(5, label_path)
    with pytest.raises(TypeError):
        model.load_dataset_from_directory_with_csv_labels(im_path, 5)
    with pytest.raises(ValueError):
        model.load_dataset_from_directory_with_csv_labels(os.path.join(test_data_dir, 'test_dir_csv_images', ''),
                                                          label_path)
    model.load_dataset_from_directory_with_csv_labels(im_path, label_path)


def test_load_ippn_leaf_count_dataset_from_directory(test_data_dir):
    # The following tests take the format laid out in the documentation of an example
    # for training a leaf counter, and leave out key parts to see if the program
    # throws an appropriate exception, or executes as intended due to using a default setting
    data_path = os.path.join(test_data_dir, 'test_Ara2013_Canon', '')

    # forgetting to set image dimensions
    model = dpp.RegressionModel(debug=False, save_checkpoints=False, report_rate=20)
    # channels = 3
    model.set_batch_size(4)
    # model.set_image_dimensions(128, 128, channels)
    model.set_resize_images(True)
    model.set_num_regression_outputs(1)
    model.set_test_split(0.1)
    model.set_weight_initializer('xavier')
    model.set_maximum_training_epochs(1)
    model.set_learning_rate(0.0001)
    with pytest.raises(RuntimeError):
        model.load_ippn_leaf_count_dataset_from_directory(data_path)

    # forgetting to set num epochs
    model = dpp.RegressionModel(debug=False, save_checkpoints=False, report_rate=20)
    channels = 3
    model.set_batch_size(4)
    model.set_image_dimensions(128, 128, channels)
    model.set_resize_images(True)
    model.set_num_regression_outputs(1)
    model.set_test_split(0.1)
    model.set_weight_initializer('xavier')
    # model.set_maximum_training_epochs(1)
    model.set_learning_rate(0.0001)
    with pytest.raises(RuntimeError):
        model.load_ippn_leaf_count_dataset_from_directory(data_path)

    # the following shouldn't raise any issues since there should be defaults for
    # batch_size, train_test_split, and learning_rate
    model = dpp.RegressionModel(debug=False, save_checkpoints=False, report_rate=20)
    channels = 3
    # model.set_batch_size(4)
    model.set_image_dimensions(128, 128, channels)
    model.set_resize_images(True)
    model.set_num_regression_outputs(1)
    # model.set_train_test_split(0.8)
    model.set_weight_initializer('xavier')
    model.set_maximum_training_epochs(1)
    # model.set_learning_rate(0.0001)
    model.load_ippn_leaf_count_dataset_from_directory(data_path)


# seems to be some issue with tensorflow not using the same graph when run inside pytest framework
# def test_begin_training():
#     model = dpp.DPPModel(debug=False, save_checkpoints=False, report_rate=20)
#     channels = 3
#     model.set_batch_size(4)
#     model.set_image_dimensions(128, 128, channels)
#     model.set_resize_images(True)
#     model.set_problem_type('regression')
#     model.set_num_regression_outputs(1)
#     model.set_train_test_split(0.8)
#     model.set_weight_initializer('xavier')
#     model.set_maximum_training_epochs(1)
#     model.set_learning_rate(0.0001)
#     model.load_ippn_leaf_count_dataset_from_directory('test_data/Ara2013-Canon')
#     model.add_input_layer()
#     model.add_convolutional_layer(filter_dimension=[5, 5, channels, 32], stride_length=1, activation_function='tanh')
#     model.add_pooling_layer(kernel_size=3, stride_length=2)
#
#     model.add_convolutional_layer(filter_dimension=[5, 5, 32, 64], stride_length=1, activation_function='tanh')
#     model.add_pooling_layer(kernel_size=3, stride_length=2)
#
#     model.add_convolutional_layer(filter_dimension=[3, 3, 64, 64], stride_length=1, activation_function='tanh')
#     model.add_pooling_layer(kernel_size=3, stride_length=2)
#
#     model.add_convolutional_layer(filter_dimension=[3, 3, 64, 64], stride_length=1, activation_function='tanh')
#     model.add_pooling_layer(kernel_size=3, stride_length=2)
#     model.add_output_layer()
#     model.begin_training()
