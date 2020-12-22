node('master') {
  def version = "latest"
  def name = "jenkins-ci"
  def dockerRegistry = "jfrog.it-academy.by/public"
  def registryCredential = "jfrog-sa"
  def image

  stage ("Checkout") {
    checkout scm
  }

  stage ("Docker: Build") {
      image = docker.build(
              "${dockerRegistry}/${name}:${version}",
              "--network=host .",
      )
  }

  stage ("Docker: Push") {
        docker.withRegistry('https://jfrog.it-academy.by', registryCredential) {
          image.push "${version}"
          echo "Docker Image pushed: ${dockerRegistry}/${name}:${version}"
        }
  }
}