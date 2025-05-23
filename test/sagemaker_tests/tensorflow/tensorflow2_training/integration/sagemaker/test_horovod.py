# Copyright 2017-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import absolute_import

import os

import pytest

import sagemaker
from sagemaker.instance_group import InstanceGroup
from sagemaker.tensorflow import TensorFlow

from ..... import invoke_sm_helper_function
from ...integration.utils import processor, py_version, unique_name_from_base  # noqa: F401

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "resources")


@pytest.mark.integration("horovod")
@pytest.mark.model("mnist")
@pytest.mark.team("frameworks")
@pytest.mark.multinode(2)
def test_distributed_training_horovod(
    ecr_image, sagemaker_regions, instance_type, tmpdir, framework_version, sm_below_tf213_only
):
    invoke_sm_helper_function(
        ecr_image,
        sagemaker_regions,
        _test_distributed_training_horovod_function,
        instance_type,
        tmpdir,
        framework_version,
    )


def _test_distributed_training_horovod_function(
    ecr_image, sagemaker_session, instance_type, tmpdir, framework_version
):
    mpi_options = "-verbose -x orte_base_help_aggregate=0"
    estimator = TensorFlow(
        entry_point=os.path.join(RESOURCE_PATH, "mnist", "horovod_mnist.py"),
        role="SageMakerRole",
        instance_type=instance_type,
        instance_count=2,
        image_uri=ecr_image,
        framework_version=framework_version,
        py_version="py3",
        hyperparameters={
            "sagemaker_mpi_enabled": True,
            "sagemaker_mpi_custom_mpi_options": mpi_options,
            "sagemaker_mpi_num_of_processes_per_host": 1,
        },
        sagemaker_session=sagemaker_session,
    )

    estimator.fit(job_name=unique_name_from_base("test-tf-horovod"))

    model_data_source = sagemaker.local.data.get_data_source_instance(
        estimator.model_data, sagemaker_session
    )

    for filename in model_data_source.get_file_list():
        assert os.path.basename(filename) == "model.tar.gz"


@pytest.mark.integration("horovod")
@pytest.mark.model("mnist")
@pytest.mark.team("frameworks")
@pytest.mark.multinode(2)
@pytest.mark.skip_cpu
def test_hc_distributed_training_horovod(
    ecr_image, sagemaker_regions, instance_type, tmpdir, framework_version, sm_below_tf213_only
):
    instance_type = instance_type or "ml.g5.12xlarge"
    training_group = InstanceGroup("train_group_1", instance_type, 2)
    invoke_sm_helper_function(
        ecr_image,
        sagemaker_regions,
        _test_hc_distributed_training_horovod_function,
        [training_group],
        tmpdir,
        framework_version,
    )


def _test_hc_distributed_training_horovod_function(
    ecr_image, sagemaker_session, instance_groups, tmpdir, framework_version
):
    mpi_options = "-verbose -x orte_base_help_aggregate=0"
    estimator = TensorFlow(
        entry_point=os.path.join(RESOURCE_PATH, "mnist", "horovod_mnist.py"),
        role="SageMakerRole",
        image_uri=ecr_image,
        instance_groups=instance_groups,
        framework_version=framework_version,
        py_version="py3",
        hyperparameters={
            "sagemaker_mpi_enabled": True,
            "sagemaker_mpi_custom_mpi_options": mpi_options,
            "sagemaker_mpi_num_of_processes_per_host": 1,
        },
        sagemaker_session=sagemaker_session,
    )

    estimator.fit(job_name=unique_name_from_base("test-tf-hc-horovod"))

    model_data_source = sagemaker.local.data.get_data_source_instance(
        estimator.model_data, sagemaker_session
    )

    for filename in model_data_source.get_file_list():
        assert os.path.basename(filename) == "model.tar.gz"


@pytest.mark.integration("horovod")
@pytest.mark.multinode(2)
@pytest.mark.team("frameworks")
@pytest.mark.model("unknown_model")
def test_distributed_training_horovod_with_env_vars(
    ecr_image, sagemaker_regions, instance_type, tmpdir, framework_version, sm_below_tf213_only
):
    invoke_sm_helper_function(
        ecr_image,
        sagemaker_regions,
        _test_distributed_training_horovod_with_env_vars_function,
        instance_type,
        tmpdir,
        framework_version,
    )


def _test_distributed_training_horovod_with_env_vars_function(
    ecr_image, sagemaker_session, instance_type, tmpdir, framework_version
):
    mpi_options = "-verbose -x orte_base_help_aggregate=0"
    estimator = TensorFlow(
        entry_point=os.path.join(RESOURCE_PATH, "hvdbasic", "train_hvd_env_vars.py"),
        role="SageMakerRole",
        instance_type=instance_type,
        instance_count=2,
        image_uri=ecr_image,
        framework_version=framework_version,
        py_version="py3",
        hyperparameters={
            "sagemaker_mpi_enabled": True,
            "sagemaker_mpi_custom_mpi_options": mpi_options,
            "sagemaker_mpi_num_of_processes_per_host": 2,
        },
        sagemaker_session=sagemaker_session,
    )

    estimator.fit(job_name=unique_name_from_base("test-tf-horovod-env-vars"))
