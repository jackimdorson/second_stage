#Standard Lib
import logging


def setup_logger():
    logger = logging.getLogger('my_logger')   # ロガーの作成
    logger.setLevel(logging.DEBUG)    # ログレベルを設定, DEBUGレベル以上の全てのログメッセージが記録される
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   # フォーマッターの作成(logメッセージのフォーマットasctime=TimeStamp, name=LoggerName, levelname=LogLevel)

    console_handler = logging.StreamHandler()   # コンソールハンドラーの作成
    console_handler.setLevel(logging.DEBUG)     # コンソールのログレベルを設定
    console_handler.setFormatter(formatter)     # フォーマッターを設定

    file_handler = logging.FileHandler('app.log')  #ファイルハンドラーの作成
    file_handler.setLevel(logging.DEBUG)           #ファイルのログレベルを設定
    file_handler.setFormatter(formatter)           #フォーマッターを設定

    logger.addHandler(console_handler)  #ロガーにハンドラーを追加
    logger.addHandler(file_handler)     #ログmsgの出力　
    return logger         #logger.debug('詳細なデバッグ情報') logger.info('一般的な情報')
    #logger.warning('警告msg')　logger.error('エラーmsg')　logger.critical('重大なmsg')


logger = setup_logger()