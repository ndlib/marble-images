FROM alpine:3.11.6

RUN apk update && apk upgrade

# basic packages libvips
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
	libgsf-dev \
	poppler-glib

# text rendering, PDF rendering, SVG rendering
RUN apk add \
	gdk-pixbuf-dev \
	poppler-dev \
	librsvg-dev

# install vips
ARG VIPS_VERSION=8.9.2
ARG VIPS_URL=https://github.com/libvips/libvips/releases/download

RUN wget -O- ${VIPS_URL}/v${VIPS_VERSION}/vips-${VIPS_VERSION}.tar.gz | tar xzC /tmp
RUN cd /tmp/vips-${VIPS_VERSION} \
	&& ./configure --prefix=/usr --disable-static --disable-debug \
	&& make V=0 \
	&& make install

# install fonts for PDF processing
RUN apk --no-cache add msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f

RUN apk add \
	python3-dev \
	py3-pip

# install python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install wheel --no-cache-dir
COPY image/requirements.txt /usr/local/bin/
RUN pip3 install -r /usr/local/bin/requirements.txt

# install image processing code
WORKDIR /usr/local/bin/
COPY image/ .
RUN chmod u+x process_images.py
ENTRYPOINT ["process_images.py"]
