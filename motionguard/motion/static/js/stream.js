const video = document.getElementById('video');

navigator.mediaDevices.getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    setInterval(() => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append('frame', blob);

        fetch('/receive_frame/', {
          method: 'POST',
          body: formData
        });
      }, 'image/jpeg');
    }, 300); // send every 300ms

  })
  .catch((err) => {
    console.error('Camera error: ', err);
  });
