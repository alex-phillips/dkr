#----------------------
# Parse makefile arguments
#----------------------
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

VERSION := $(shell curl -sX GET "https://api.github.com/repos/Telmate/terraform-provider-proxmox/releases/latest" | awk '/tag_name/{print $$4;exit}' FS='[""]' | sed 's/v//g')


#----------------------
# Terminal
#----------------------

GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

#------------------------------------------------------------------
# - Add the following 'help' target to your Makefile
# - Add help text after each target name starting with '\#\#'
# - A category can be added with @category
#------------------------------------------------------------------

HELP_FUN = \
	%help; \
	while(<>) { \
		push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
		print "-----------------------------------------\n"; \
		print "| Control sandbox stack\n"; \
		print "|\n"; \
		print "| usage: make [command]\n"; \
		print "-----------------------------------------\n\n"; \
		for (sort keys %help) { \
			print "${WHITE}$$_:${RESET \
		}\n"; \
		for (@{$$help{$$_}}) { \
			$$sep = " " x (32 - length $$_->[0]); \
			print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
		}; \
		print "\n"; \
	}

help: ##@other Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

#----------------------
# Build docker-compose.yml
#----------------------
install: ##@init Install Proxmox plugins
	wget https://github.com/Telmate/terraform-provider-proxmox/releases/download/v$(VERSION)/terraform-provider-proxmox_$(VERSION)_linux_amd64.zip
	mkdir -p /tmp/tf-proxmox-setup
	unzip -o -d /tmp/tf-proxmox-setup terraform-provider-proxmox_$(VERSION)_linux_amd64.zip
	mkdir -p $$HOME/.terraform.d/plugins/registry.example.com/telmate/proxmox/1.0.0/linux_amd64
	mv /tmp/tf-proxmox-setup/terraform-provider-proxmox_v$(VERSION) $$HOME/.terraform.d/plugins/registry.example.com/telmate/proxmox/1.0.0/linux_amd64/
	rm -rf terraform-provider-proxmox_* /tmp/tf-proxmox-setup
