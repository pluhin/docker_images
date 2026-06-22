## Busy-box

- based on Ubuntu 22.04
- mc vim curl wget git telnet netcat

## Build and push image 

You can set tag to build and push image. Example for the tag:

```bash
jenkins:v1.2.3
```

Pipeline will create image `jenkins` with tag `v1.2.3` and publish it to the **ghcr** registry
