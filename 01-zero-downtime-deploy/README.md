# 무중단 배포 실험 (kind)

## 0. 환경 설정
    cd ~/k8s-labs/01-zero-downtime-deploy

## 1. 클러스터 + 이미지
    kind create cluster --name graceful-lab --config ./kind-config.yaml
    kubectl config use-context kind-graceful-lab
    docker build -t fastapi-graceful:1 app/
    kind load docker-image fastapi-graceful:1 --name graceful-lab
    # kube-proxy 설정 확인
    kubectl -n kube-system get cm kube-proxy -o yaml | grep -A6 "iptables:"

## 2. 실험 A (안전하지 않은 설정)
    kubectl apply -f ./manifests/deploy-a.yaml
    kubectl rollout status deploy/web
    kubectl apply -f ./manifests/loadgen.yaml
    kubectl logs -f loadgen                 # 정상 로그(code=200)가 쌓이는지 확인
    # 다른 터미널에서 배포 트리거
    kubectl rollout restart deploy/web
    kubectl get pods -w
    # 배포가 끝나고 ~30초 뒤 집계
    kubectl logs loadgen | grep -o 'code=[0-9]*' | sort | uniq -c
    kubectl logs loadgen | grep -v 'code=200'

## 3. 실험 B (안전한 설정): 같은 순서로 반복
    kubectl delete pod loadgen
    kubectl apply -f ./manifests/deploy-b.yaml
    kubectl rollout status deploy/web
    kubectl apply -f ./manifests/loadgen.yaml
    kubectl logs -f loadgen                 # 정상 로그(code=200)가 쌓이는지 확인
    # 다른 터미널에서 배포 트리거
    kubectl rollout restart deploy/web
    kubectl get pods -w
    # 배포가 끝나고 ~30초 뒤 집계
    kubectl logs loadgen | grep -o 'code=[0-9]*' | sort | uniq -c

## 4. 정리
    kind delete cluster --name graceful-lab