# openRuyi replacement for cmake/external_projects/triton_kernels.cmake.
#
# Upstream fetches the OpenAI triton_kernels .py sources from the triton git
# repository at configure time (FetchContent GIT_REPOSITORY https://github.com/
# triton-lang/triton.git), which needs network and git that the OBS builder does
# not have. triton_kernels is an optional MoE helper (its setup.py extension is
# marked optional), so ship an empty vllm/third_party/triton_kernels instead and
# keep the offline build working — mirroring python-torch dropping optional GPU
# fetches such as aotriton.
#
# setup.py copies vllm/third_party/triton_kernels unconditionally for HIP builds,
# so the (empty) directory must still be created and installed under the
# triton_kernels install component.
add_custom_target(triton_kernels)
install(CODE "file(MAKE_DIRECTORY \"\${CMAKE_INSTALL_PREFIX}/vllm/third_party/triton_kernels\")"
        COMPONENT triton_kernels)
