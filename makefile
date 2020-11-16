.PHONY: ssh, deploy, pub, build

ssh:
	mosh --ssh="ssh -i ~/.ssh/cl" -- ubuntu@$(PISERVER) tmux new -A -s remote

deploy:
	ansible-playbook bootstrap.yml -i $(PISERVER), -e ansible_user=ubuntu
