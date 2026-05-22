%bcond test 0

# Header only package
%global debug_package %{nil}

Summary:        Header-only library for using Keras (TensorFlow) models in C++
Name:           frugally-deep
License:        MIT
# Main license is MIT
# BSD-2-Clause is only for cmake/HunterGate.cmake and that is not distributed
Version:        0.15.30
Release:        1%{?dist}

URL:            https://github.com/Dobiasd/frugally-deep
Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  eigen3
BuildRequires:  fplus-devel
#BuildRequires:  nlohmann_json-devel
BuildRequires:  nlohmann-json
BuildRequires:  gcc-c++

%description
Would you like to build/train a model using Keras/Python? And would
you like to run the prediction (forward pass) on your model in C++
without linking your application against TensorFlow? Then
frugally-deep is exactly for you.

frugally-deep

* is a small header-only library written in modern and pure C++.
* is very easy to integrate and use.
* depends only on FunctionalPlus, Eigen and json - also header-only
  libraries.
* supports inference (model.predict) not only for sequential models
  but also for computational graphs with a more complex topology,
  created with the functional API.
* re-implements a (small) subset of TensorFlow, i.e., the operations
  needed to support prediction.
* results in a much smaller binary size than linking against TensorFlow.
* works out-of-the-box also when compiled into a 32-bit executable.
  (Of course, 64 bit is fine too.)
* avoids temporarily allocating (potentially large chunks of)
  additional RAM during convolutions (by not materializing the im2col
  input matrix).
* utterly ignores even the most powerful GPU in your system and uses
  only one CPU core per prediction. ;-)
* but is quite fast on one CPU core, and you can run multiple
  predictions in parallel, thus utilizing as many CPUs as you like
  to improve the overall prediction throughput of your
  application/pipeline.

%package devel

Summary:        Header-only library for using Keras (TensorFlow) models in C++
Provides:       %{name}-static = %{version}-%{release}

%description devel
Would you like to build/train a model using Keras/Python? And would
you like to run the prediction (forward pass) on your model in C++
without linking your application against TensorFlow? Then
frugally-deep is exactly for you.

frugally-deep

* is a small header-only library written in modern and pure C++.
* is very easy to integrate and use.
* depends only on FunctionalPlus, Eigen and json - also header-only
  libraries.
* supports inference (model.predict) not only for sequential models
  but also for computational graphs with a more complex topology,
  created with the functional API.
* re-implements a (small) subset of TensorFlow, i.e., the operations
  needed to support prediction.
* results in a much smaller binary size than linking against TensorFlow.
* works out-of-the-box also when compiled into a 32-bit executable.
  (Of course, 64 bit is fine too.)
* avoids temporarily allocating (potentially large chunks of)
  additional RAM during convolutions (by not materializing the im2col
  input matrix).
* utterly ignores even the most powerful GPU in your system and uses
  only one CPU core per prediction. ;-)
* but is quite fast on one CPU core, and you can run multiple
  predictions in parallel, thus utilizing as many CPUs as you like
  to improve the overall prediction throughput of your
  application/pipeline.

%prep
%autosetup -p1 -n %{name}-%{version}

# cmake changed
sed -i -e 's@cmake_minimum_required(VERSION 3.2)@cmake_minimum_required(VERSION 3.5)@' CMakeLists.txt

%build
%cmake 
%cmake_build

%if %{with test}
%check
%ctest
%endif

%install
%cmake_install

%files devel
%dir %_includedir/fdeep
%dir %_libdir/cmake/%{name}
%license LICENSE
%doc README.md
%_includedir/fdeep/*
%_libdir/cmake/%{name}/*

%changelog
* Mon Feb 2 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 0.15.30-1
- Import from upstream
