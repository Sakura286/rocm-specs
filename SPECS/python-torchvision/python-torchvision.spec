# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname torchvision
%global llvm_maj_ver 22

# The default flavor builds against CPU-only torch. The "rocm" multibuild
# flavor builds HIP operators against python-torch-rocm.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "rocm"
%bcond rocm 1
%global toolchain clang
%else
%bcond rocm 0
%endif

%bcond test 0

# Upstream metadata names torch, while openRuyi deliberately exposes the CPU
# and ROCm runtimes as distinct RPMs. Require the matching flavor explicitly.
%global __requires_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)

%if %{with rocm}
Name:           python-%{srcname}-rocm
%else
Name:           python-%{srcname}
%endif
Version:        0.28.0
Release:        %autorelease
Summary:        Image and video datasets for torch deep learning
License:        BSD-3-Clause AND BSD-2-Clause AND MIT
URL:            https://github.com/pytorch/vision
VCS:            git:%{url}.git
# The GitHub release has no attached source asset; use the release tag archive.
#!RemoteAsset:  sha256:ecc4451241c8eeadc0c88213bd65c7932c9622d1d0034254b938f25362283ee9
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(prep):  -n vision-%{version}
BuildOption(install):  %{srcname}
# torchvision.image is a torch operator library, not an importable Python module.
BuildOption(check):  -e '%{srcname}.image'
# torchvision.io.video re-exports Meta-internal pytorch.vision.fb code that is
# intentionally unavailable in OSS builds.
BuildOption(check):  -e '%{srcname}.io.video'

BuildRequires:  ninja
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pillow)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(requests)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
%if %{with test}
BuildRequires:  python3dist(pytest)
%endif
%if %{with rocm}
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hipsolver)
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(rocm-core)
BuildRequires:  cmake(rocprim)
BuildRequires:  cmake(rocthrust)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  hipcc
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  python-torch-rocm-devel
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%else
BuildRequires:  gcc-c++
BuildRequires:  python-torch-devel
%endif

Requires:       python3dist(numpy)
Requires:       python3dist(pillow)
Requires:       python3dist(requests)
%if %{with rocm}
Requires:       python-torch-rocm
Provides:       python3-%{srcname}-rocm = %{version}-%{release}
Provides:       python3-%{srcname}-rocm%{?_isa} = %{version}-%{release}
Conflicts:      python-%{srcname}
%else
Requires:       python-torch
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}
Conflicts:      python-%{srcname}-rocm
%endif

%patchlist
# Report the ROCm version through torchvision's existing CUDA-version operator.
2000-Add-HIP-version-detection.patch
# The matching torch flavor is supplied by static BuildRequires below.
2001-Use-flavor-specific-torch-build-dependency.patch

%description
The torchvision package consists of popular datasets, model architectures,
and common image transformations for computer vision.

%prep -a
# Keep useful debug information in the native extensions.
sed -i -e 's@extra_compile_args["cxx"].append("-g0")@extra_compile_args["cxx"].append("-g")@' setup.py

%generate_buildrequires
# Runtime dependencies are listed explicitly, including the matching torch flavor.
%pyproject_buildrequires -R

%build -p
export TORCHVISION_USE_WEBP=1
%if %{with rocm}
# OBS workers do not expose a GPU, so force compilation of the HIP operators.
export FORCE_CUDA=1
export ROCM_HOME=%{_prefix}
export HIP_CLANG_PATH=%{rocmllvm_bindir}
export PATH=%{rocmllvm_bindir}:$PATH
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}
%endif

%install -a
# Python modules are not executable scripts; remove accidental shebangs.
for f in `find %{buildroot}%{python3_sitearch} -name '*.py'`; do
    if [ ! -x $f ]; then
        sed -i '1{\@^#!/usr/bin@d}' $f
    fi
done

%check -a
PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}" \
PYTHONDONTWRITEBYTECODE=1 \
%{__python3} -sP - <<'PY'
import torch
import torchvision

assert torchvision.extension._has_ops()
boxes = torch.tensor([[0.0, 0.0, 2.0, 2.0], [0.5, 0.5, 1.5, 1.5]])
scores = torch.tensor([0.9, 0.8])
assert torchvision.ops.nms(boxes, scores, 0.5).tolist() == [0, 1]
PY
%if %{with test}
%pytest
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
