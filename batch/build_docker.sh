region="ap-northeast-2"
ecr="008747557116.dkr.ecr.ap-northeast-2.amazonaws.com"
docker_name="catalog-connector"
tag="latest"

name="subeans"
password="subin8860"

aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${ecr}
docker build --build-arg "NAME=${name}" \
             --build-arg "PASSWORD=${password}" \
             -t "${docker_name}" . --no-cache

docker tag "${docker_name}:${tag}" "${ecr}/${docker_name}:${tag}"
docker push "${ecr}/${docker_name}:${tag}"
