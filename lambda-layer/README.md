Helper for creating lambda layer

# create folder structure
> mkdir -p python/lib/python3.9/site-packages

# lambda layer create
> docker run -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.9" /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.9/site-packages/; exit"

# lambda layer zip
> zip -r mypythonlibs.zip python > /dev/null