#!/usr/bin/with-contenv bash

distro=""
arch=""

if [[ -f /usr/bin/apt ]]; then
    distro="debian"
elif [[ -f /sbin/apk ]]; then
    distro="alpine"
elif [[ -f /usr/bin/dnf ]]; then
    distro="fedora"
elif [[ -f /usr/sbin/pacman ]]; then
    distro="arch"
fi

case "$distro" in
"debian")
    arch=$(dpkg --print-architecture)
    ;;
"alpine")
    arch=$(uname -m)
    ;;
"fedora")
    echo "Fedora is currently not supported."
    exit 1
    ;;
"arch")
    echo "ArchLinux is currently not supported."
    exit 1
    ;;
esac

until [ -f /cert/mitmproxy-ca-cert.cer ]; do
    sleep 2
    echo "no cert yet"
done
if [ ! -d "/mitm" ]; then

    mkdir -p /mitm
    cp /cert/mitmproxy* /mitm
    chmod +rx /mitm/mitmproxy*

    echo -n "/mitm/mitmproxy-ca.pem" >/run/s6/container_environment/CURL_CA_BUNDLE

    if [ $distro == "debian" ]; then
        mkdir -p /usr/share/ca-certificates/mitm
        cp /mitm/mitmproxy-ca-cert.cer /usr/share/ca-certificates/mitm/mitmproxy-ca.cer
        chmod 644 /usr/share/ca-certificates/mitm/mitmproxy-ca.cer
        echo "mitm/mitmproxy-ca.cer" >>/etc/ca-certificates.conf
        update-ca-certificates
        echo "Updated debian store"
    fi

    if [ $distro == "alpine" ]; then
        cat /mitm/mitmproxy-ca-cert.cer >>/etc/ssl/certs/ca-certificates.crt
        echo "Updated alpine store"
    fi

    if [ -x "$(command -v python3)" ]; then #https://incognitjoe.github.io/adding-certs-to-requests.html
        echo -n "/mitm/mitmproxy-ca.pem" >/run/s6/container_environment/REQUESTS_CA_BUNDLE
        echo -n "/mitm/mitmproxy-ca.pem" >/run/s6/container_environment/SSL_CERT_FILE
        python3 -c '
try:
    import certifi
    cafile = certifi.where()
    with open("/mitm/mitmproxy-ca.pem", "rb") as infile:
        customca = infile.read()
    with open(cafile, "ab") as outfile:
        outfile.write(customca)
    print("Installed certifi cert")
except ImportError:
    pass
'
    fi

    javaversions="/usr/lib/jvm/java-8-openjdk-$arch/jre/lib/security /usr/lib/jvm/java-11-openjdk-$arch/jre/lib/security /usr/lib/jvm/java-11-openjdk-$arch/lib/security /usr/lib/jvm/java-17-openjdk-$arch/lib/security /config/data/keystore"

    for javaver in $javaversions; do
        if [ -f "$javaver/cacerts" ]; then
            keytool -importcert -trustcacerts -keystore "$javaver/cacerts" \
                -storepass changeit -noprompt -alias mmitm -file /mitm/mitmproxy-ca-cert.pem
            echo "Added cert to $javaver keystore"
        fi
    done

    if [ -x "$(command -v php)" ]; then
        sed -i 's#;curl.cainfo=#curl.cainfo=/mitm/mitmproxy-ca-cert.cer#' /etc/php*/php.ini
        sed -i 's#;openssl.cafile=#openssl.cafile=/mitm/mitmproxy-ca-cert.cer#' /etc/php*/php.ini
        echo "Updated php store"
    fi

fi

while ! nc -z localhost 42069; do
    sleep 0.5
done

s6-setuidgid abc curl -I -s -w "%{http_code}\n" -o /dev/null -x http://localhost:42069 https://www.google.com || echo "Curl to mitm failed"
s6-setuidgid abc curl -I -s -w "%{http_code}\n" -o /dev/null https://www.linuxserver.io

