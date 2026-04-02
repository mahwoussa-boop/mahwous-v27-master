import logging
import os
import sys

def configure_logging(level=None):
    """
    إعداد التسجيل (Logging) الموحد للمشروع V27.
    المستوى الافتراضي هو INFO، يمكن تغييره عبر متغير البيئة MAHWOUS_LOG_LEVEL.
    """
    if level is None:
        level_str = os.environ.get("MAHWOUS_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # المخرجات إلى الكونسول (Console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # الإعداد العام
    root = logging.getLogger()
    root.setLevel(level)
    
    # تنظيف الهاندلرز القديمة لمنع التكرار
    if root.hasHandlers():
        root.handlers.clear()
        
    root.addHandler(console_handler)

    # تجاهل رسائل المكتبات الخارجية المزعجة
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logging.info(f"تم إعداد نظام التسجيل الموحد V27 بالمستوى: {logging.getLevelName(level)}")

def get_logger(name):
    """اللحصول على لوجر باسم الوحدة"""
    return logging.getLogger(name)
