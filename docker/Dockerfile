FROM alpine:3.11.6

RUN apk update && apk upgrade

# basic packages libvips likes
RUN apk add \
	build-base \
	autoconf \
	automake \
	libtool \
	bc \
	zlib-dev \
	expat-dev \
	jpeg-dev \
	tiff-dev \
	glib-dev \
	libjpeg-turbo-dev \
	libexif-dev \
	lcms2-dev \
	fftw-dev \
	giflib-dev \
	libpng-dev \
	libwebp-dev \
	orc-dev \
	libgsf-dev

# text rendering, PDF rendering, SVG rendering
RUN apk add \
	gdk-pixbuf-dev \
	poppler-dev \
	librsvg-dev

# install vips
ARG VIPS_VERSION=8.8.3
ARG VIPS_URL=https://github.com/libvips/libvips/releases/download

RUN wget -O- ${VIPS_URL}/v${VIPS_VERSION}/vips-${VIPS_VERSION}.tar.gz | tar xzC /tmp
RUN cd /tmp/vips-${VIPS_VERSION} \
	&& ./configure --prefix=/usr --disable-static --disable-debug \
	&& make V=0 \
	&& make install

RUN apk add \
	python3-dev \
	py3-pip

# and now pyvips can go on
RUN pip3 install --upgrade pip
RUN pip3 install wheel --no-cache-dir
RUN pip3 install pyvips boto3 oauth2client==4.1.3 google==2.0.2 \
	google-api-python-client==1.7.11 google-auth-httplib2==0.0.3 \
	google-auth-oauthlib==0.4.0

COPY process_images.py /usr/local/bin/
RUN chmod u+x /usr/local/bin/process_images.py
ENTRYPOINT ["process_images.py"]