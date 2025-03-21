import cv2
import subprocess
import numpy as np

# libcamera-vid를 이용해 영상을 파이프로 가져오기
command = ['libcamera-vid', '--inline', '--nopreview', '-t', '0', '--codec', 'mjpeg', '-o', '-']

# 파이프 열기
pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

jpeg_data = b""

# 비디오 저장 설정 (코덱, 파일명, FPS, 해상도)
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 코덱 설정
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))  # 파일명, FPS, 해상도

# OpenCV로 MJPEG 스트림 읽기
while True:
    # 한 번에 적당한 양의 데이터를 읽어들임
    data = pipe.stdout.read(1024)
    if not data:
        break

    # JPEG 데이터 수집
    jpeg_data += data

    # JPEG 파일이 완성됐는지 확인 (JPEG 종료 마커: 0xFFD9)
    if b'\xff\xd9' in jpeg_data:
        # 완전한 JPEG 이미지가 있을 때만 처리
        jpeg_end = jpeg_data.index(b'\xff\xd9') + 2
        jpeg_frame = jpeg_data[:jpeg_end]
        jpeg_data = jpeg_data[jpeg_end:]

        # numpy 배열로 변환 후 OpenCV로 읽기
        np_arr = np.frombuffer(jpeg_frame, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # 영상 출력
        if frame is not None:
            cv2.imshow('Camera', frame)

            # 파일로 프레임 저장
            out.write(frame)

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 모든 작업이 끝나면 해제
pipe.terminate()
out.release()  # 비디오 파일 저장 완료
cv2.destroyAllWindows()

