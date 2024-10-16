FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

RUN apt update && apt install -y git

RUN useradd -m containeruser
RUN chown -R containeruser /opt/conda
USER containeruser

COPY --chown=containeruser src /home/containeruser/src
COPY --chown=containeruser config /home/containeruser/config

WORKDIR /home/containeruser

# run pip install with 'no caching' to reduce space
RUN pip install --no-cache-dir -r src/requirements.txt
 
CMD ["python", "src/main.py"]
