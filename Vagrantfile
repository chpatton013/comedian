mirrorlist_url = "https://www.archlinux.org/mirrorlist"
mirrorlist_params = "country=US&protocol=https&use_mirror_status=on"
$provision = <<-PROVISION
curl --silent '#{mirrorlist_url}/?#{mirrorlist_params}' |
  sed --expression 's/^#Server/Server/' >/etc/pacman.d/mirrorlist
pacman --sync --refresh --noconfirm make python python-pip
systemctl start docker.service
systemctl enable docker.service

cat <<PROFILE >/etc/profile.d/comedian.sh
export PYTHONDONTWRITEBYTECODE=1
PROFILE
PROVISION

Vagrant.configure("2") do |config|
  config.vm.box = "archlinux/archlinux"
  config.vm.provision "shell", inline: $provision
end
