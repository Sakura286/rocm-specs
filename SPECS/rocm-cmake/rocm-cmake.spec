# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
# SPDX-FileContributor: misaka00251 <liuxin@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# there is no debug package - this is just cmake modules
%global debug_package %{nil}

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}
%global source_tag therock-%{rocm_release}

Name:           rocm-cmake
Version:        %{rocm_version}
Release:        %autorelease
Summary:        CMake modules for common build and development tasks for ROCm
License:        MIT
URL:            https://github.com/ROCm/rocm-cmake
#!RemoteAsset:  sha256:41b034780028684a3ee281fcc2b8ed0573a64b55a5ef38d10bb59deddd3d9710
Source:         %{url}/archive/refs/tags/%{source_tag}.tar.gz
BuildArch:      noarch
BuildSystem:    cmake

# https://github.com/ROCm/rocm-cmake/issues/276
Patch0:         0001-rocm-cmake-follow-cmake-install-rules.patch
# Keep upstream test paths explicit and tolerate intentional absolute test installs.
Patch1:         2000-make-tests-independent-of-system-libdir.patch
# The version suffix is empty when a release archive has no Git history.
Patch2:         2001-fix-release-archive-version-test.patch

BuildOption(prep):  -n %{name}-%{source_tag}
# PRIVATE/PREFIX tests assume upstream's non-FHS layout; version-parent requires
# Git history absent from release archives; documentation tools are not packaged.
BuildOption(check):  -E '^pass-(doc-sphinxdoxygen|libprivate|simple-prefix|version-parent)$'

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  git-core

Requires:       cmake

%description
rocm-cmake is a collection of CMake modules for common build and development
tasks within the ROCm project. It is therefore a build dependency for many of
the libraries that comprise the ROCm platform.

rocm-cmake is not required for building libraries or programs that use ROCm; it
is required for building some of the libraries that are a part of ROCm.

%prep -a

# Fix hardcoding of libdir
sed -i -e "s@set(CMAKE_INSTALL_LIBDIR \"lib\"@set(CMAKE_INSTALL_LIBDIR \"%{_lib}\"@" share/rocmcmakebuildtools/cmake/ROCMCreatePackage.cmake
sed -i -e "s@set(CMAKE_INSTALL_LIBDIR \"lib\"@set(CMAKE_INSTALL_LIBDIR \"%{_lib}\"@" share/rocmcmakebuildtools/cmake/ROCMInstallTargets.cmake

%check -p
# Version tests create local Git repositories inside the isolated build tree.
export GIT_AUTHOR_NAME="CHEN Xuan" GIT_AUTHOR_EMAIL="chenxuan@iscas.ac.cn"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
export GIT_CEILING_DIRECTORIES="%{_builddir}"

%install -a

rm -f %{buildroot}%{_prefix}/share/doc/rocm-cmake/LICENSE

%files
%doc CHANGELOG.md
%license LICENSE
%dir %{_datadir}/rocm
%dir %{_datadir}/rocmcmakebuildtools
%{_datadir}/rocm/*
%{_datadir}/rocmcmakebuildtools/*

%changelog
%autochangelog
