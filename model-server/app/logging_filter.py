import re, json, logging
SENSITIVE_KEYS = {"password","secret","token","key","aws_secret_access_key","authorization"}
class MaskFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = json.loads(record.getMessage())
            for k in list(msg.keys()):
                if k.lower() in SENSITIVE_KEYS: msg[k] = "******"
            record.msg = json.dumps(msg, ensure_ascii=False)
        except Exception:
            # 간단 문자열에서 비밀번호 패턴 마스킹
            record.msg = re.sub(r'(?i)(password|secret|token)\s*[:=]\s*[^,\s]+', r'\1=******', str(record.getMessage()))
        return True
