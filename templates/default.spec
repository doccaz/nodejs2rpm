%define base_name {{ __BASENAME__ }}
%define nodejs_dir %{_libdir}/node_modules/npm
%define nodejs_modulesdir %{nodejs_dir}/node_modules

# to avoid empty debugfiles error on some distros
%global debug_package %{nil}

Name:            nodejs-%{base_name}
Version:         {{ __VERSION__ }}
Release:         0
License:         {{ __LICENSE__ }}
Summary:         {{ __SUMMARY__ }}
URL:             {{ __URL__|replace('git+https','https')|replace('git://','http://') }}
Group:           Development/Languages/Other
Source0:         http://registry.npmjs.org/%{base_name}/-/%{base_name}-%{version}.tgz
Requires:        nodejs
BuildRequires:   nodejs
BuildRequires:   nodejs-packaging
%if ! %{defined fedora}
BuildRequires:	 npm
%endif
BuildRoot:       %{_tmppath}/%{name}-%{version}-%{release}-root
#BuildArch:       noarch
ExclusiveArch:   %{ix86} x86_64 %{arm} noarch
Provides:	 npm(%{base_name}) = %{version}
AutoReqProv:	no
Requires:	npm(code)
Requires:	npm(errno)
Requires:	npm(syscall)
Requires:	npm(getaddrinfo)
{%- if __REQUIRES__ %}
{%- for req,ver in __REQUIRES__|dictsort %}
Requires:	npm({{ req }}) >= {{ ver|replace('~', '')|replace('x', '0')|replace('^','') }}
{%- endfor %}
{%- endif %}

%description
{% if __BOILERPLATE__ %}
{{__BOILERPLATE__}}

{{ __DESCRIPTION__ }}
{% else %}
{{ __DESCRIPTION__ }}
{%endif %}

%prep
%setup -q -n package

%build

%install
mkdir -p %{buildroot}%{nodejs_modulesdir}/%{base_name}
mv -f package.json \
        %{buildroot}%{nodejs_modulesdir}/%{base_name}

cp -prf * \
        %{buildroot}%{nodejs_modulesdir}/%{base_name}

%clean
rm -rf $RPM_BUILD_ROOT

%post 

# if it's an installation, register it with npm
if [ $1 == 1 ]; then
	cd %{nodejs_modulesdir}
	npm install %{base_name} --save
fi

%postun

# if it's an uninstallation, unregister from npm
if [ $1 == 0 ]; then
	cd %{nodejs_modulesdir}
	npm uninstall %{base_name} --save
fi

%files
%defattr(0644,root,root,-)
%dir %{nodejs_dir}
%dir %{nodejs_modulesdir}
%{nodejs_modulesdir}/%{base_name}/*
%dir %{nodejs_modulesdir}/%{base_name}
{%- if __DOC__ != "none" %}
%doc {{ __DOC__ }}
{%- endif %}

%changelog

