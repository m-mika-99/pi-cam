import sys
import time
import datetime

import cv2


def main():
    ######################
    # TODO 👇👇configから読み込みたい
    ######################
    # カメラID
    camera_id = 0
    # 表示ウィンドウ名
    window_name = 'frame'
    # 捕捉しなくなってから何秒間録画するか？
    after_cap_time_sec = 3
    # 保存ファイルコーデック
    # TODO 選択したい
    codec = cv2.VideoWriter.fourcc(*"mp4v")
    # 保存先ディレクトリ
    # TODO 文字じゃなくPathで持ちたい
    rec_dir_name = "./output"

    # TODO 👆configここまで👆

    # カメラ読み込み
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        # カメラ取得できず、、、
        # TODOエラーログ/Exception
        print("カメラからデータ取れずエラー")
        sys.exit(1)
    # カメラのフレームレート
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # 捕捉終了後の撮影フレーム数
    after_cap_frames = after_cap_time_sec * fps

    # キー入力まち用
    delay = 1
    # 録画中フラグ
    is_recording = False
    # 捕捉終了後何フレーム撮影したかのカウンタ
    counter = 0
    # 検知用データ初期化
    before = None
    # レコーダ
    recoder = None

    #################################
    # メインループ
    #################################
    while True:
        # 画像読み込み
        ret, frame = cap.read()
        if not ret:
            # 読み込めなかった場合
            continue

        #################################
        # 動体検知
        #################################
        # グレースケール化
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if before is None:
            before = gray.astype("float")
            continue
        # 現在のフレームと移動平均との差を計算
        cv2.accumulateWeighted(gray, before, 0.5)
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(before))
        # frame_deltaの画像を2値化
        thresh = cv2.threshold(frame_delta, 3, 255, cv2.THRESH_BINARY)[1]
        # 輪郭のデータを得る
        contours = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )[0]
        # 差分があった点を画面に描く
        obj_cnt = 0 # 検出オブジェクト数の記録
        for target in contours:
            x, y, w, h = cv2.boundingRect(target)
            # 小さな変更点は無視 TODO サイズ
            if w < 50:
                continue
            obj_cnt += 1
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        #################################
        # 撮影開始・継続・終了判定
        #################################
        # 直前情報保持
        is_recording_before = is_recording
        if obj_cnt >= 1:
            # 捕捉中は撮影する
            is_recording = True
            # カウンタは初期化
            counter = 0
        else:
            # 捕捉してない
            if not is_recording_before:
                # 撮影してないときはそのまま
                pass
            elif counter <= after_cap_frames:
                # 撮影していてカウンター規定値以内なら撮影継続
                counter += 1
            else:
                # カウンターが振り切ったら撮影終了
                is_recording = False

        #################################
        # 撮影開始・終了処理
        #################################
        if is_recording and not is_recording_before:
            print("撮影開始") # TODO デバッグ用
            # 開始時刻
            rec_start_time = datetime.datetime.now()
            # レコーダ作成 TODO ファイル名
            recoder = cv2.VideoWriter(
                f"{rec_dir_name}/{rec_start_time.strftime('%Y%m%d-%H%M%S')}.mp4",
                codec,
                20.0,
                (640, 480)
            )
        elif not is_recording and is_recording_before:
            print("撮影終了") # TODO デバッグ用
            # レコーダ開放
            recoder.release()
        elif is_recording and is_recording_before:
            # TODO 撮影が一定期間継続したらファイル切りたい
            pass

        #################################
        # 撮影
        #################################
        if is_recording:
            recoder.write(frame)

        # TODO デバッグ用：録画中表示
        if is_recording:
            cv2.putText(
                frame,
                text='NowRecording',
                org=(20, 20),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.0,
                color=(0, 0, 255),
                thickness=2,
                lineType=cv2.LINE_4
            )

        #################################
        # TODO DEBUG:映像出力
        #################################
        # ウィンドウでの再生速度を元動画と合わせる
        time.sleep(1 / fps)
        # ウィンドウで表示
        cv2.imshow(window_name, frame)

        #################################
        # 終了
        #################################
        # キー入力「q」で終了
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    #################################
    # リソースお片付け
    #################################
    # カメラ
    cap.release()
    # 表示ウィンドウ
    cv2.destroyAllWindows()
    # レコーダ
    if recoder:
        recoder.release()

if __name__ == '__main__':
    main()
