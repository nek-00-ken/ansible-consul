# -*- mode: ruby -*-
# vi: set ft=ruby :
#

Vagrant.configure(2) do |config|

  config.vm.synced_folder "synced_folder", "/tmp/synced_folder"
  config.vm.provision "shell", inline: 'cat /tmp/synced_folder/vagrant_rsa.pub >> /home/vagrant/.ssh/authorized_keys'

  config.vm.define "server-1" do |machine|
    machine.vm.hostname = "server-1"
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.network "private_network", ip: "192.168.10.10"
    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end

  config.vm.define "client-1" do |machine|
    machine.vm.hostname = "client-1"
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.network "private_network", ip: "192.168.10.21"
    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end

  config.vm.define "client-2" do |machine|
    machine.vm.hostname = "client-2"
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.network "private_network", ip: "192.168.10.22"
    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end

  config.vm.define "client-3" do |machine|
    machine.vm.hostname = "client-3"
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.network "private_network", ip: "192.168.10.23"
    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end

  config.vm.define "client-4" do |machine|
    machine.vm.hostname = "client-4"
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.network "private_network", ip: "192.168.10.24"
    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end

  config.vm.define "client-5" do |machine|
    machine.vm.hostname = "client-5"
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.network "private_network", ip: "192.168.10.25"
    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end
end
