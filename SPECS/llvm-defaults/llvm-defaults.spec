# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Downstream override of Base's llvm-defaults, trimmed to only the libomp
# subpackages.  Base ships /usr/lib64/libomp.so as a dangling symlink into
# llvm22/lib64/ (the real runtime lives under llvm22/lib/%{_target_platform}/),
# which breaks every clang -fopenmp binary at load time; this rebuild fixes the
# symlink target.  We deliberately do NOT rebuild the clang/llvm/... subpackages
# here: OBS prefers a project-local build over the inherited Base one, so a full
# override would shadow Base with a fresh (low) autorelease and trip clang22's
# "Obsoletes: clang-rpm-macros < 22-13".  Keeping only libomp/libomp-devel lets
# Base provide everything else untouched while our fixed libomp still wins by
# local preference.  Drop the whole override once Base carries the fix.

%global maj_ver 22

Name:           llvm-defaults
Version:        %{maj_ver}
Release:        %{autorelease}
Summary:        Default LLVM %{maj_ver} OpenMP runtime symlinks
License:        Apache-2.0 WITH LLVM-exception OR NCSA
URL:            http://llvm.org

BuildRequires:  libomp%{maj_ver}
BuildRequires:  libomp%{maj_ver}-devel

%description
This package provides default unversioned symlinks for the LLVM %{maj_ver}
OpenMP runtime libraries.

# ============================================================================
# libomp subpackage
# ============================================================================
%package     -n libomp
Summary:        Default LLVM OpenMP runtime libraries
Requires:       libomp%{maj_ver} > %{maj_ver}

%description -n libomp
This package provides default unversioned symlinks for LLVM OpenMP runtime
libraries %{maj_ver}.

# ============================================================================
# libomp-devel subpackage
# ============================================================================
%package     -n libomp-devel
Summary:        Default LLVM OpenMP development files
Requires:       libomp%{maj_ver}-devel > %{maj_ver}
Requires:       libomp = %{version}-%{release}

%description -n libomp-devel
This package provides default unversioned symlinks for LLVM OpenMP development
files %{maj_ver}.

# ============================================================================
# Install section - create symlinks
# ============================================================================
%install
mkdir -p %{buildroot}%{_libdir}/cmake

# libomp symlinks
# The llvm%{maj_ver} OpenMP runtime lives under the per-target subdir
# llvm%{maj_ver}/lib/%{_target_platform}/ (e.g. .../lib/x86_64-openruyi-linux/),
# not llvm%{maj_ver}/%{_lib}/.  The Base spec pointed these at
# llvm%{maj_ver}/lib64/libomp.so, which does not exist, so /usr/lib64/libomp.so
# was a dangling symlink and any clang -fopenmp binary (e.g. python-torch) failed
# to load libomp.so at runtime.  Point them at the real per-target path.
ln -sfn llvm%{maj_ver}/lib/%{_target_platform}/libarcher.so %{buildroot}%{_libdir}/libarcher.so
ln -sfn llvm%{maj_ver}/lib/%{_target_platform}/libomp.so    %{buildroot}%{_libdir}/libomp.so
ln -sfn llvm%{maj_ver}/lib/%{_target_platform}/libompd.so   %{buildroot}%{_libdir}/libompd.so
ln -sfn ../llvm%{maj_ver}/lib/%{_target_platform}/cmake/openmp %{buildroot}%{_libdir}/cmake/openmp

# ============================================================================
# Files section
# ============================================================================
%files -n libomp
%{_libdir}/libarcher.so
%{_libdir}/libomp.so
%{_libdir}/libompd.so

%files -n libomp-devel
%{_libdir}/cmake/openmp

%changelog
%autochangelog
