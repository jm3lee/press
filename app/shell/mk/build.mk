# Deprecated wrapper for legacy builds
$(warning app/shell/mk/build.mk is deprecated; use ../../makefile)
include $(dir $(lastword $(MAKEFILE_LIST)))../../../makefile
