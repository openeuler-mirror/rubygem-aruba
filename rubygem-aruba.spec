%global gem_name aruba
Summary:             CLI Steps for Cucumber, hand-crafted for you in Aruba
Name:                rubygem-%{gem_name}
Version:             0.14.9
Release:             2
License:             MIT
URL:                 https://github.com/cucumber/aruba
Source0:             http://rubygems.org/gems/%{gem_name}-%{version}.gem
Patch0:              Replace-problematic-AnsiColor-module-with-simple.patch
Patch1:              Silence-keyword-argument-warnings-on-Ruby-2.7.patch
BuildRequires:       ruby(release) rubygems-devel ruby rubygem(cucumber) >= 1.3.19
BuildRequires:       rubygem(childprocess) >= 0.5.6 rubygem(ffi) >= 1.9.10 rubygem(minitest)
BuildRequires:       rubygem(pry) rubygem(rspec) >= 3 rubygem(contracts) >= 0.9
BuildRequires:       rubygem(thor) >= 0.19 /usr/bin/python3 ruby-irb
BuildArch:           noarch
%description
Aruba is Cucumber extension for Command line applications written
in any programming language.

%package doc
Summary:             Documentation for %{name}
Requires:            %{name} = %{version}-%{release}
BuildArch:           noarch
%description doc
Documentation for %{name}

%prep
%setup -q -n %{gem_name}-%{version}
%gemspec_remove_dep -g childprocess '>= 0.6.3'
%patch0 -p1
%patch1 -p1

%build
gem build ../%{gem_name}-%{version}.gemspec
%gem_install

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/
rm -f %{buildroot}%{gem_cache}
pushd %{buildroot}%{gem_instdir}
rm -rf \
	.[^.]* \
	Gemfile \
	Rakefile \
	appveyor.yml \
	%{gem_name}.gemspec \
	cucumber.yml \
	config/ \
	fixtures/ \
	spec/ \
	script/ \
	%{nil}

%check
pushd .%{gem_instdir}
rm .rspec
sed -i spec/spec_helper.rb \
	-e '\@[sS]imple[Cc]ov@d' \
	-e '\@[Bb]undler@d' \
	%{nil}
RUBYOPT=-rtime rspec spec
sed -i features/support/env.rb \
	-e '\@require.*simplecov@d'
> features/support/simplecov_setup.rb
sed -i fixtures/cli-app/spec/spec_helper.rb \
	-e "\@\$LOAD_PATH@s|\.\./\.\./lib|$(pwd)/lib|"
sed -i features/steps/command/shell.feature \
	-e 's|zsh|bash|' \
	-e '\@echo.*Hello.*c@s|echo|echo -e|'
if ! grep -q python3 features/steps/command/shell.feature
then
	sed -i features/steps/command/shell.feature -e 's|python|python3|'
	sed -i features/steps/command/shell.feature -e "s|python'|python3'|"
	sed -i lib/aruba/generators/script_file.rb  \
		-e '\@interpreter@s|A-Z|A-Z0-9|'
	sed -i features/getting_started/run_commands.feature \
		-e '\@[^-]python@s|python|python3|'
fi
sed -i Rakefile \
	-e '\@[Bb]undler@d' \
	-e 's|bundle exec ||' \
	%{nil}
sed -i features/api/core/expand_path.feature -e "s|/home/\[\^/\]+|$(echo $HOME)|"
sed -i features/configuration/home_directory.feature \
	-e "\@Scenario: Default value@,\@Scenario@s|/home/|$(echo $HOME)|"
sed -i features/configuration/home_directory.feature \
	-e "\@Set to aruba's working directory@,\@Scenario@s|/home/|$(echo $HOME)/|"
RUBYOPT=-I$(pwd)/lib cucumber
popd

%files
%dir %{gem_instdir}
%license %{gem_instdir}/LICENSE
%doc %{gem_instdir}/README.md
%{gem_libdir}
%{gem_instdir}/bin/
%exclude %{gem_instdir}/config
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/CONTRIBUTING.md
%doc %{gem_instdir}/CHANGELOG.md
%doc %{gem_instdir}/TODO.md
%{gem_instdir}/doc/
%{gem_instdir}/features/
%{gem_instdir}/templates/

%changelog
* Mon Feb 21 2022 liyanan <liyanan32@huawei.com> - 0.14.9-2
- fix build error

* Wed Aug 19 2020 shenleizhao <shenleizhao@huawei.com> - 0.14.9-1
- package init
