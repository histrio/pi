.PHONY: ssh, deploy, pub, build

ssh:
	mosh --ssh="ssh -i ~/.ssh/cl" -- pi@$(PISERVER) tmux new -A -s remote

deploy:
	ansible-playbook bootstrap.yml -i $(PISERVER), -e ansible_user=pi

force-deploy:
	ansible-playbook local.yml -i $(PISERVER), -e ansible_user=pi
