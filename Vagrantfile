# -*- mode: ruby -*-

Vagrant.configure('2') do |config|
  config.vm.box = 'fgrehm/trusty64-lxc'

  config.vm.provider :lxc do |lxc|
    # Same effect as 'customize ["modifyvm", :id, "--memory", "1024"]' for VirtualBox
    lxc.customize 'cgroup.memory.limit_in_bytes', '4096M'
  end

  config.vm.hostname = 'dev'
  config.vm.network "forwarded_port", guest: 80, host: 8000
  config.vm.network "forwarded_port", guest: 8888, host: 8888

  config.vm.provision :shell, inline: 'sudo apt-get install -y redir'

  config.vm.synced_folder 'airports', '/home/vagrant/app'
  config.vm.synced_folder 'salt/roots', '/srv'

  config.ssh.forward_agent = true

  config.vm.provision :salt do |salt|
    salt.minion_config = 'salt/minion.conf'
    salt.run_highstate = true
    salt.verbose = true
  end
end
