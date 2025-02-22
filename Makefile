# Help target - lists available commands
help:
	@echo "Available commands:"

# Deploy to RS Connect
.PHONY: deploy-rsconnect
deploy-rsconnect:
	rsconnect deploy shiny . --name lightbridge-ks --title radreportparser \
	--exclude _data-test/ \
	--exclude _dev/ \
	--exclude .vscode/ \
	--exclude README.md



# Default target (runs when you just type 'make')
.DEFAULT_GOAL := help