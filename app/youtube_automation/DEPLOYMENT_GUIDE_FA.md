# سیستم اتوماسیون یوتیوب نسخه 3.0 - راهنمای استقرار

**حق چاپ © 2025 سعید علادینی. تمامی حقوق محفوظ است.**

این راهنما دستورالعمل‌های جامعی را برای استقرار سیستم اتوماسیون یوتیوب نسخه 3.0 بر روی سرور ارائه می‌دهد، که عمدتاً بر روی راه‌اندازی مبتنی بر Docker تمرکز دارد. این نسخه شامل یک زیرساخت اصلی قوی، نقاط پایانی API و پیاده‌سازی‌های استاب (Stub) برای تولید محتوا، ساخت ویدیو و آپلود است که امکان تست سرتاسری را در یک محیط شبیه‌سازی شده فراهم می‌کند.

## 🎯 نمای کلی پروژه

سیستم اتوماسیون یوتیوب نسخه 3.0 به عنوان یک پلتفرم ماژولار و مقیاس‌پذیر برای تولید و انتشار خودکار محتوای یوتیوب طراحی شده است. این سیستم از FastAPI برای API، SQLAlchemy برای ORM، PostgreSQL برای پایگاه داده، Redis برای کشینگ و صف‌بندی وظایف، و Celery برای پردازش وظایف ناهمزمان استفاده می‌کند. کل سیستم با استفاده از Docker کانتینری شده و با Docker Compose ارکستراسیون می‌شود.

## 🚀 شروع سریع (Docker Compose)

این روش توصیه شده برای استقرار است که یک محیط ایزوله و به راحتی قابل مدیریت را فراهم می‌کند.

### پیش‌نیازها

اطمینان حاصل کنید که سرور شما موارد زیر را نصب کرده است:

-   **Docker:** [راهنمای نصب](https://docs.docker.com/engine/install/)
-   **Docker Compose:** [راهنمای نصب](https://docs.docker.com/compose/install/)

### مراحل نصب

1.  **انتقال پروژه:**
    بسته `youtube_automation_v3.zip` را به سرور خود آپلود کنید. می‌توانید از `scp`، `rsync` یا هر روش امن انتقال فایل دیگری استفاده کنید.

    ```bash
    # مثال با استفاده از scp (با جزئیات سرور و مسیر محلی خود جایگزین کنید)
    scp /path/to/local/youtube_automation_v3.zip ubuntu@your_server_ip:~/
    ```

2.  **استخراج پروژه:**
    از طریق SSH به سرور خود متصل شوید و آرشیو پروژه را استخراج کنید.

    ```bash
    ssh ubuntu@your_server_ip
    unzip ~/youtube_automation_v3.zip -d /home/ubuntu/
    cd /home/ubuntu/youtube_automation_v3
    ```

3.  **پیکربندی متغیرهای محیطی:**
    پروژه از متغیرهای محیطی برای پیکربندی استفاده می‌کند. یک فایل الگو `.env.example` ارائه شده است.

    ```bash
    cp .env.example .env
    ```

    **فایل `.env` را با استفاده از یک ویرایشگر متن مانند `nano` یا `vim` ویرایش کنید:**

    ```bash
    nano .env
    ```

    **متغیرهای کلیدی برای پیکربندی:**

    -   `JWT_SECRET_KEY`: یک رشته قوی و تصادفی برای امضای توکن‌های JWT. می‌توانید با `openssl rand -hex 32` یکی تولید کنید.
    -   `SECRET_KEY`: یک رشته قوی و تصادفی دیگر برای امنیت عمومی برنامه.
    -   `POSTGRES_PASSWORD`: یک رمز عبور قوی برای کاربر PostgreSQL تنظیم کنید.
    -   `REDIS_PASSWORD`: یک رمز عبور قوی برای Redis تنظیم کنید.
    -   `AI_PROVIDER`: ارائه‌دهنده AI خود را انتخاب کنید (`ollama`، `openai`، `deepseek`). `ollama` برای توسعه محلی رایگان توصیه می‌شود.
        -   اگر `ollama`، `OLLAMA_BASE_URL` و `OLLAMA_MODEL` را پیکربندی کنید.
        -   اگر `openai` یا `deepseek`، `OPENAI_API_KEY` یا `DEEPSEEK_API_KEY` را ارائه دهید.
    -   `LOG_LEVEL`: برای تولید `INFO` و برای توسعه `DEBUG` را تنظیم کنید.
    -   `CORS_ORIGINS`: برای دامنه برنامه فرانت‌اند خود تنظیم کنید (مثلاً `http://localhost:3000,https://your-frontend.com`). استفاده از `*` فقط برای توسعه است.

4.  **ساخت و راه‌اندازی سرویس‌ها:**
    به دایرکتوری ریشه پروژه (`/home/ubuntu/youtube_automation_v3`) بروید و از Docker Compose برای ساخت ایمیج‌ها و راه‌اندازی همه سرویس‌ها استفاده کنید.

    ```bash
    docker compose build
    docker compose up -d
    ```

    -   `docker compose build`: ایمیج‌های Docker را برای همه سرویس‌های تعریف شده در `docker-compose.yml` می‌سازد.
    -   `docker compose up -d`: سرویس‌ها را در حالت جدا شده (detached mode) راه‌اندازی می‌کند (در پس‌زمینه اجرا می‌شوند).

5.  **بررسی وضعیت سرویس:**
    بررسی کنید که آیا همه کانتینرها به درستی در حال اجرا هستند.

    ```bash
    docker compose ps
    ```

    باید وضعیت `Up` را برای `web`، `db`، `redis`، `celery_worker` و `celery_beat` مشاهده کنید.

6.  **دسترسی به API:**
    برنامه FastAPI در پورت `8000` سرور شما قابل دسترسی خواهد بود.

    -   **بررسی سلامت (Health Check):** `http://your_server_ip:8000/health`
    -   **مستندات API (Swagger UI):** `http://your_server_ip:8000/docs`
    -   **مستندات API (ReDoc):** `http://your_server_ip:8000/redoc`

## 🔧 جزئیات پیکربندی

برای لیست کامل متغیرهای محیطی قابل پیکربندی و توضیحات آنها به فایل `.env.example` مراجعه کنید.

## 📊 مهاجرت‌های پایگاه داده (Alembic)

این پروژه از Alembic برای مهاجرت‌های پایگاه داده استفاده می‌کند. پس از راه‌اندازی اولیه، در صورت وجود تغییرات در شمای پایگاه داده، باید مهاجرت‌ها را اجرا کنید.

1.  **دسترسی به شل سرویس `web`:**
    ```bash
    docker compose exec web bash
    ```

2.  **اجرای مهاجرت‌ها:**
    ```bash
    alembic upgrade head
    ```

    *توجه: برای راه‌اندازی اولیه، `Base.metadata.create_all(bind=engine)` در `main.py` ایجاد جداول را مدیریت می‌کند. Alembic برای تغییرات شمای بعدی است.* 

## 🐛 عیب‌یابی

### مشکلات رایج

-   **کانتینر راه‌اندازی نمی‌شود:** لاگ‌های سرویس مربوطه را بررسی کنید.
    ```bash
    docker compose logs <service_name>
    # مثال: docker compose logs web
    ```

-   **دستور `docker compose` یافت نشد:** اطمینان حاصل کنید که Docker Compose به درستی نصب شده و در PATH شما قرار دارد.

-   **`no configuration file provided`:** اطمینان حاصل کنید که در دایرکتوری `youtube_automation_v3` هستید یا از پرچم `-f` استفاده کنید (مثلاً `docker compose -f docker-compose.yml up -d`).

-   **خطاهای اتصال به پایگاه داده:** `POSTGRES_USER`، `POSTGRES_PASSWORD`، `POSTGRES_DB` را در فایل `.env` خود بررسی کنید و اطمینان حاصل کنید که سرویس `db` در حال اجرا است.

-   **Celery worker/beat به Redis متصل نمی‌شود:** `REDIS_PASSWORD` را بررسی کنید و اطمینان حاصل کنید که سرویس `redis` در حال اجرا است.

### راه‌اندازی مجدد سرویس‌ها

```bash
# راه‌اندازی مجدد یک سرویس خاص
docker compose restart <service_name>

# راه‌اندازی مجدد همه سرویس‌ها
docker compose restart

# توقف همه سرویس‌ها
docker compose stop

# توقف و حذف همه کانتینرها، شبکه‌ها و ولوم‌ها
docker compose down
```

## 📚 مراحل بعدی

پس از استقرار، می‌توانید با استفاده از اسکریپت تست ارائه شده یا مستقیماً از طریق Swagger UI (`/docs`)، نقاط پایانی API را تست کنید.

---
