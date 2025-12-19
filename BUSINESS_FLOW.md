# 🎯 FLOW BISNIS & AUTH SYSTEM

## 1. SISTEM OTENTIKASI & AKSES

### 1.1 Role Sistem
```
├─ Admin Sistem          → Akses penuh (tidak harus warga)
├─ Ketua RW              → Supervisi di level RW
├─ Ketua RT              → Supervisi di level RT
├─ Sekretaris            → Input data & dokumentasi
├─ Bendahara             → Manage keuangan
└─ Warga                 → User biasa
```

### 1.2 Warga dapat Login Jika:
```
✓ Akun sudah dibuat admin/ketua RT
   └─ Resident status = "aktif" (sudah di-assign ke family)
   └─ User sudah di-link ke resident
   └─ Direct login

✓ Mendaftar sendiri (self-registration)
   └─ Register via mobile app
   └─ Resident status = "pending" + ResidentApproval pending
   └─ Tunggu RT/RW review & approve + assign family
   └─ Setelah approve → status = "aktif"
   └─ Baru bisa login
```

### 1.3 Auth Endpoints

**POST /auth/login**
```json
Request:
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "Admin",
    "username": "admin",
    "email": "admin@example.com",
    "phone": "08123456789",
    "role": "admin",
    "resident_id": null,
    "created_at": "2025-01-01T00:00:00"
  }
}
```

**POST /auth/register** (Self Registration)
```json
Request:
{
  "nik": "3271234567890123",
  "family_number": "1234567890123456",
  "name": "Adi Wijaya",
  "gender": "Laki-laki",
  "birth_place": "Jakarta",
  "birth_date": "1995-05-15",
  "username": "adi_wijaya",
  "email": "adi@example.com",
  "phone": "08987654321",
  "password": "password123",
  "password_confirm": "password123"
}

Response:
{
  "id": 101,
  "name": "Adi Wijaya",
  "username": "adi_wijaya",
  "email": "adi@example.com",
  "phone": "08987654321",
  "role": "warga",
  "resident_id": 50,
  "created_at": "2025-01-01T10:00:00"
}

Status Code: 201 Created
Note: 
  - User baru role = "warga" default
  - Resident baru status = "pending" (menunggu approval RT)
  - Family otomatis di-create/di-assign dari family_number
  - Jika family_number belum ada → create family baru
  - Jika family_number sudah ada → assign ke family yang ada
  - ResidentApproval record dibuat otomatis (pending_approval)
```

**GET /auth/me** (Require Auth)
```
Header: Authorization: Bearer <access_token>

Response:
{
  "id": 1,
  "name": "Admin",
  "username": "admin",
  "email": "admin@example.com",
  "phone": "08123456789",
  "role": "admin",
  "resident_id": null,
  "resident": null
}
```

**POST /auth/refresh** (Require Auth)
```
Header: Authorization: Bearer <access_token>

Response: TokenResponse (sama seperti login)
```

**POST /auth/logout** (Require Auth)
```
Response: {"message": "Logout successful"}
Note: Logout di client-side (hapus token)
```

---

## 2. SISTEM KEPENDUDUKAN

### 2.1 Pendaftaran Warga (Mandiri atau Input Admin/RT)

**Flow Pendaftaran Mandiri (Self-Registration via Mobile App):**
```
1. Warga isi form → POST /auth/register
   {
     "nik": "3271234567890123",
     "family_number": "KEL-001",  # Nomor keluarga dari KK
     "name": "Adi Wijaya",
     "gender": "Laki-laki",
     "birth_date": "1995-05-15",
     "birth_place": "Jakarta",
     "username": "adi_wijaya",
     "email": "adi@example.com",
     "phone": "08987654321",
     "password": "password123",
     "password_confirm": "password123"
   }

2. Sistem validasi:
   ├─ Check birth_date: apakah >= 17 tahun?
   ├─ JIKA < 17 tahun: REJECT dengan pesan "Anak-anak tidak bisa self-register"
   ├─ JIKA >= 17 tahun: Lanjut ke step 3
   └─ Check: NIK sudah terdaftar? → REJECT jika sudah ada

3. Sistem trigger (Self-Registration Flow):
   ├─ Create Resident:
   │  ├─ status = "pending" ← PENDING (belum approve RT)
   │  ├─ family_id = temporary (assign nanti saat approval)
   │  ├─ nik, name, gender, birth_date, phone diisi dari form
   │  └─ ID auto-increment (misal ID = 50)
   │
   ├─ Create User (linked ke resident):
   │  ├─ username = adi_wijaya
   │  ├─ password = hash(password123)
   │  ├─ email = adi@example.com
   │  ├─ role = "warga"
   │  ├─ resident_id = 50
   │  └─ active = true (tapi belum bisa login sampai resident diapprove)
   │
   ├─ Create ResidentApproval:
   │  ├─ resident_id = 50
   │  ├─ status = "pending_approval" ← PENDING, bukan "approved"!
   │  ├─ note = "Self-registration via mobile app"
   │  └─ Simpan data family_number dari registrasi
   │
   ├─ Create activity_log (self-registration action)
   └─ Notif ke RT/RW: ada warga baru perlu approval

4. Response ke warga:
   {
     "id": 101,
     "name": "Adi Wijaya",
     "username": "adi_wijaya",
     "email": "adi@example.com",
     "resident_id": 50,
     "message": "Akun berhasil dibuat. Silakan menunggu persetujuan dari RT/RW untuk dapat login dan menggunakan aplikasi sepenuhnya."
   }

5. Warga coba login (SEBELUM approval):
   POST /auth/login
   {
     "username": "adi_wijaya",
     "password": "password123"
   }
   
   Response: ❌ BLOCKED
   {
     "error": "Akun Anda belum disetujui oleh RT/RW. Silakan tunggu persetujuan sebelum dapat login."
   }
   
   Implementasi: Check di login endpoint
   ├─ user_id = valid
   ├─ password = correct
   ├─ Cek: resident.status == "aktif"?
   └─ JIKA status != "aktif": REJECT login

6. RT/RW review pending approvals:
   GET /resident-approvals?status=pending_approval
   
   RT/RW lihat:
   ├─ Nama: Adi Wijaya
   ├─ NIK: 3271234567890123
   ├─ Umur: 30 tahun (dari birth_date)
   ├─ Family Number: KEL-001
   ├─ Status Approval: Menunggu Persetujuan
   └─ Verifikasi via KK (Kartu Keluarga)

7. RT/RW approve & assign family:
   PUT /resident-approvals/{id}
   {
     "status": "approved",
     "family_id": 5,  # RT assign ke family existing atau create baru
     "note": "Data valid, sudah cek KK. Assigned ke family Bpk. Joko"
   }
   
   Sistem trigger:
   ├─ Update residents.status = "aktif" ← SEKARANG BISA LOGIN!
   ├─ Update residents.family_id = 5 (assign ke family)
   ├─ Update resident_approvals.status = "approved"
   ├─ Create activity_log (approval + family assignment)
   └─ Notif ke warga: "Akun Anda sudah disetujui! Silakan login untuk mulai menggunakan aplikasi."

8. Setelah approval - Warga coba login lagi:
   POST /auth/login
   {
     "username": "adi_wijaya",
     "password": "password123"
   }
   
   Response: ✅ SUCCESS
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer",
     "expires_in": 1800,
     "user": {
       "id": 101,
       "name": "Adi Wijaya",
       "username": "adi_wijaya",
       "resident_id": 50,
       "role": "warga"
     }
   }

9. Jika RT reject:
   PUT /resident-approvals/{id}
   {
     "status": "rejected",
     "note": "NIK tidak valid / data tidak sesuai KK"
   }
   
   Sistem trigger:
   ├─ Delete dari resident_approvals (record ini)
   ├─ Delete dari residents (hapus resident record)
   ├─ Delete dari users (hapus user account)
   ├─ Create activity_log (rejection + deletion action)
   └─ Notif ke warga: "Akun Anda ditolak dan dihapus. Alasan: {note}. Silakan hubungi RT untuk informasi lebih lanjut."

10. Warga yang di-reject coba login:
    POST /auth/login
    {
      "username": "adi_wijaya",
      "password": "password123"
    }
    
    Response: ❌ BLOCKED
    {
      "error": "Username atau password salah"
    }
    
    (User sudah tidak ada di sistem)

11. Opsi untuk warga yang di-reject:
    
    a) ✅ BISA re-register dengan NIK sama
       └─ Karena semua data sudah dihapus (NIK tidak unique lagi)
       └─ Warga bisa register ulang dari awal
       └─ Baru di-approve/reject oleh RT lagi
    
    b) Hubungi RT untuk clarify data (optional)
       └─ Sebelum register ulang lagi
       └─ Fix masalahnya (misal NIK yang benar)

12. Flow Register Ulang:
    POST /auth/register
    {
      "nik": "3271234567890123",  # NIK yang sama, tapi sekarang bisa (sudah dihapus)
      "name": "Adi Wijaya",
      "username": "adi_wijaya",     # Username sama juga boleh (sudah dihapus)
      ...
    }
    
    Sistem:
    ├─ NIK tidak duplicate (user lama sudah dihapus)
    ├─ Create Resident baru (ID baru, misal ID = 51)
    ├─ Create User baru (ID baru)
    ├─ Create ResidentApproval baru (status = "pending_approval")
    ├─ Create activity_log (self-registration baru)
    └─ Notif ke RT: ada warga baru (lagi) perlu approval

**REJECT FLOW DIAGRAM (dengan deletion):**
```
┌─────────────────────────────────────────────────────────────┐
│ Warga Register via /auth/register                           │
│ ├─ Resident: status = "pending", ID = 50                    │
│ ├─ User: username = adi_wijaya, ID = 101                    │
│ └─ Approval: status = "pending_approval"                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─ RT APPROVE
                       │  ├─ residents.status = "aktif"
                       │  ├─ approvals.status = "approved"
                       │  ├─ family_id assigned
                       │  └─ Warga bisa login ✅
                       │
                       └─ RT REJECT
                          ├─ DELETE residents WHERE id = 50
                          ├─ DELETE users WHERE id = 101
                          ├─ DELETE resident_approvals WHERE resident_id = 50
                          ├─ Create activity_log (reject + deletion)
                          │
                          └─ Warga Options:
                             ├─ A: Hubungi RT (optional clarify)
                             └─ B: Register ulang dengan NIK/username sama
                                 ├─ NIK sudah tidak unique (user lama dihapus)
                                 ├─ Create Resident baru (ID = 51)
                                 ├─ Create User baru (ID = 102)
                                 └─ Waiting approval lagi ⏳
```

**DATA YANG DIHAPUS SAAT REJECT:**
```sql
-- Sebelum reject:
residents:     id=50, nik=..., name=..., status="pending"
users:         id=101, username=..., email=...
approvals:     id=(some), resident_id=50, status="pending_approval"

-- Sesudah reject (DELETE):
residents:     (HAPUS semua record id=50)
users:         (HAPUS semua record id=101)
approvals:     (HAPUS semua record resident_id=50)

-- Sisa di activity_logs (untuk audit):
activity_logs: action="reject_warga", 
               actor_id=RT_user_id, 
               target_id=50, 
               description="Rejected: NIK tidak valid"
```

**KEY POINT:**
- ✅ Data langsung dihapus saat reject (clean slate)
- ✅ NIK & username bisa dipakai lagi (unique constraint cleared)
- ✅ Warga bisa register ulang dari awal
- ✅ Activity log tetap tercatat (untuk audit trail)
- ✅ Tidak ada "ditolak" status di database (hanya di log)
- ✅ Simple & clean, tidak ada zombie data

**KEY DIFFERENCES - Admin Add vs Self-Register:**
```
┌──────────────────────┬─────────────────────────┬──────────────────────────┐
│ Aspek                │ Admin Add (/residents)  │ Self-Register (/register)│
├──────────────────────┼─────────────────────────┼──────────────────────────┤
│ Approval Status      │ "approved" (auto)       │ "pending_approval"       │
│ Status Warga         │ "aktif"                 │ "pending"                │
│ User Created         │ Yes (auto)              │ Yes (user input)         │
│ Password             │ Generated random        │ User set sendiri         │
│ Bisa Login           │ Ya (langsung)           │ Tidak (tunggu approval)  │
│ Family Assignment    │ Admin assign saat add   │ RT assign saat approval  │
│ Workflow             │ Create → Approval ✓     │ Create → Pending → Approval
│ User Role            │ "warga" atau custom     │ "warga" (default)        │
│ Activity Flow        │ Skip review step        │ RT harus review & approve
└──────────────────────┴─────────────────────────┴──────────────────────────┘
```

**IMPLEMENTATION CHECKLIST:**
✅ Backend auto-approve untuk admin add
🔄 Backend login gate: check resident.status == "aktif"
🔄 Self-register endpoint: POST /auth/register
🔄 Approval workflow: RT review & approve/reject
🔄 Notification system: notif saat status changed
```

**Flow Input Admin/RT (Direct Input dari Desktop):**
```
1. Admin/RT input residents langsung
   POST /residents
   {
     "family_id": 5,
     "nik": "3271234567890123",
     "name": "Adi Wijaya",
     "gender": "Laki-laki",
     "birth_date": "1995-05-15",
     "birth_place": "Jakarta",
     "phone": "08123456789",
     "status": "aktif"  # Langsung aktif, tidak perlu approval
   }

2. Sistem trigger (NEW - Auto Approve):
   ├─ Create Resident (status = "aktif", langsung terdaftar)
   ├─ Auto-Create ResidentApproval (status = "approved") ← NEW!
   │  └─ note = "Auto-approved on creation"
   ├─ Check birth_date: apakah < 17 tahun?
   │
   ├─ JIKA >= 17 tahun (DEWASA):
   │  ├─ Create User otomatis
   │  ├─ username = NIK atau generate dari name
   │  ├─ password = generated password temporary
   │  ├─ role = "warga"
   │  └─ resident_id = linked ke resident
   │
   ├─ JIKA < 17 tahun (ANAK):
   │  ├─ TIDAK create User
   │  ├─ Hanya data di tabel residents (untuk sensus)
   │  ├─ user_id = NULL
   │  └─ status = "aktif" (data saja, tidak aktif akun)
   │
   ├─ Create activity_log (resident added by admin/RT)
   └─ Notif ke warga: akun sudah dibuat (jika dewasa)

3. Warga dewasa (>= 17 tahun) login pertama kali:
   - Username: (yang di-generate admin)
   - Password: (temporary password)
   - Force password change saat login pertama
   
   Anak (< 17 tahun):
   - TIDAK punya akun
   - TIDAK bisa login
   - Data hanya untuk laporan kependudukan

**CATATAN PERUBAHAN:**
- ✅ SEBELUM: Approval dibuat dengan status = "pending_approval" (perlu approval)
- ✅ SEKARANG: Approval otomatis dibuat dengan status = "approved" (langsung aktif)
- ✅ Resident langsung tampil di list tanpa perlu approval admin lagi
- ✅ Backend ensure resident SELALU dibuat sebelum approval (transaction-safe)
```

### 2.2 Verifikasi Warga

**Tabel: resident_approvals**
```sql
id              INT PRIMARY KEY
resident_id     INT (FK to residents)
created_by      INT (FK to users - RT/RW yang input)
status          ENUM: pending_approval, approved, rejected
note            TEXT (alasan penolakan jika reject)
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**Flow Verifikasi:**
```
1. RT melihat daftar pending
   GET /resident-approvals?status=pending_approval

2. RT review data warga
   - Lihat: NIK, nama, gender, birth_date, birth_place
   - Verifikasi di KK (Kartu Keluarga)
   - Cek apakah sudah ada di keluarga mana

3. RT klik Approve & Assign Family
   PUT /resident-approvals/{id}
   {
     "status": "approved",
     "family_id": 5,  # RT harus assign ke family
     "note": "Data valid, sudah cek KK"
   }
   
   Sistem trigger:
   ├─ Update residents.status = "aktif"
   ├─ Update residents.family_id = 5
   ├─ Create activity_log (approval + family assignment)
   └─ Notif ke warga: akun approved

4. RT klik Reject
   PUT /resident-approvals/{id}
   {
     "status": "rejected",
     "note": "NIK tidak valid / sudah terdaftar"
   }
   
   Sistem trigger:
   ├─ Update residents.status = "ditolak"
   ├─ Create activity_log (rejection action)
   └─ Notif ke warga: akun ditolak + alasan
```

### 2.3 Manajemen Keluarga

**Tabel: families**
```sql
id              INT PRIMARY KEY
kk_number       VARCHAR (Nomor Kartu Keluarga - unique)
head_of_family  INT (FK to residents - kepala keluarga)
address         VARCHAR
created_by      INT (FK to users - RT/Admin yang input)
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**Tabel: residents**
```sql
id              INT PRIMARY KEY
family_id       INT (FK to families)
user_id         INT (FK to users, nullable)  # NULL jika anak (< 17 tahun)
nik             VARCHAR (unique)
name            VARCHAR
gender          VARCHAR
birth_place     VARCHAR
birth_date      DATE
phone           VARCHAR
status          VARCHAR (pending, aktif, pindah, meninggal)
created_at      TIMESTAMP
updated_at      TIMESTAMP

NOTE:
- user_id = NULL → Anak (< 17 tahun), tidak punya akun, hanya data sensus
- user_id = NOT NULL → Dewasa (>= 17 tahun), punya akun, bisa login
```

**Flow Manajemen Keluarga:**

**1. Input Kepala Keluarga + Anggota (Admin/RT):**
```
Admin/RT input keluarga baru:
POST /families
{
  "kk_number": "1234567890123456",
  "head_of_family_nik": "3271234567890123",
  "address": "Jl. Merdeka No. 5"
}

Sistem:
├─ Create family
├─ Link resident (kepala keluarga) ke family
├─ Create activity_log
└─ Notif ke keluarga

Admin/RT menambah anggota keluarga:
POST /residents
{
  "family_id": 5,
  "nik": "3271234567890124",
  "name": "Istri Kepala Keluarga",
  "gender": "Perempuan",
  "birth_date": "1996-06-20",
  "birth_place": "Jakarta",
  "phone": "08987654321"
}

Sistem: Cek birth_date

JIKA >= 17 tahun (DEWASA):
├─ Create resident (status = aktif)
├─ Create user otomatis (bisa login)
├─ Create activity_log
└─ Notif ke warga: akun dibuat

JIKA < 17 tahun (ANAK):
├─ Create resident (status = aktif)
├─ TIDAK create user (hanya data)
├─ user_id = NULL (tidak punya akun)
├─ Create activity_log
└─ Notif ke orang tua: anak sudah terdaftar
```

**2. Warga Tambah Anggota Keluarga (Self):**
```
❌ WARGA TIDAK BISA menambah keluarga sendiri
   Hanya bisa melalui:
   
   a) Admin/RT input langsung
      - Jika >= 17 tahun → Create User + bisa login
      - Jika < 17 tahun → Hanya data, tidak ada akun
      
   b) Warga dewasa (>= 17) register self
      → RT/RW approve + assign family
      → Status aktif, bisa login
      
   c) Anak (< 17 tahun) TIDAK bisa register
      → Hanya bisa di-input admin/RT

Alasan:
- Validasi data kependudukan
- RT/RW verify & assign ke family yang benar
- Anak tidak perlu akun (hanya data sensus)
- Prevent data tidak valid masuk sistem
```

**3. Perubahan Status Warga (Family Mutation):**

**Tabel: family_mutations**
```sql
id              INT PRIMARY KEY
resident_id     INT (FK to residents)
type            ENUM: pindah_masuk, pindah_keluar, meninggal
old_address     VARCHAR (nullable - jika pindah)
new_address     VARCHAR (nullable - jika pindah)
reason          TEXT
old_family_id   INT (nullable - jika pindah ke family baru)
new_family_id   INT (nullable - jika pindah ke family baru)
created_by      INT (FK to users - RT/RW)
status          ENUM: pending, approved
note            TEXT
created_at      TIMESTAMP
approved_at     TIMESTAMP
```

**Flow Mutasi:**
```
1. Warga mengajukan mutasi (pindah)
   POST /family-mutations
   {
     "type": "pindah_keluar",
     "reason": "Pindah ke luar kota",
     "new_address": "Jl. Sudirman Jakarta"
   }
   
   Atau RT/RW yang input:
   POST /family-mutations
   {
     "resident_id": 10,
     "type": "pindah_masuk",
     "new_address": "Jl. Merdeka No. 5",
     "new_family_id": 8,
     "reason": "Pindah dari keluarga lain"
   }
   
   Sistem:
   ├─ Status = pending (perlu approval)
   ├─ Create activity_log
   └─ Notif ke RT/RW

2. RT/RW review
   GET /family-mutations?status=pending

3. RT/RW approve
   PUT /family-mutations/{id}
   {
     "status": "approved",
     "note": "Disetujui"
   }
   
   Sistem trigger:
   ├─ Update residents.status (pindah/meninggal)
   ├─ Update residents.address (jika pindah)
   ├─ Update residents.family_id (jika pindah ke family baru)
   ├─ Create activity_log
   └─ Notif ke warga: mutasi disetujui

4. Jika reject
   PUT /family-mutations/{id}
   {
     "status": "rejected",
     "note": "Data tidak valid"
   }
   
   Sistem:
   ├─ Tetap pending (tidak apply)
   ├─ Create activity_log
   └─ Notif ke warga: mutasi ditolak
```

---

## 3. SISTEM PESAN WARGA

**Tabel: resident_messages**
```sql
id              INT PRIMARY KEY
resident_id     INT (FK to residents)
subject         VARCHAR
message         TEXT
status          ENUM: unread, read, resolved
created_by      INT (FK to users - warga)
reply_from      INT (FK to users - RT/RW, nullable)
reply_message   TEXT
created_at      TIMESTAMP
replied_at      TIMESTAMP
```

**Flow Pesan:**
```
1. Warga kirim pesan
   POST /resident-messages
   {
     "subject": "Pertanyaan tentang iuran",
     "message": "Bagaimana cara pembayaran iuran?"
   }
   
   Sistem:
   ├─ status = unread
   ├─ Create activity_log
   └─ Notif ke RT/RW

2. RT/RW baca pesan
   GET /resident-messages
   PUT /resident-messages/{id}
   {
     "status": "read"
   }

3. RT/RW reply
   PUT /resident-messages/{id}
   {
     "status": "resolved",
     "reply_message": "Pembayaran bisa via transfer..."
   }
   
   Sistem:
   ├─ Update reply_from, reply_message
   ├─ Create activity_log
   └─ Notif ke warga: ada reply
```

---

## 4. BROADCAST & KEGIATAN

### 4.1 Broadcast

**Tabel: broadcasts**
```sql
id              INT PRIMARY KEY
title           VARCHAR
content         TEXT
created_by      INT (FK to users - RT/RW)
broadcast_type  ENUM: announcements, urgent, info
created_at      TIMESTAMP
expires_at      TIMESTAMP (nullable - untuk temporary)
```

**Flow:**
```
1. RT/RW buat pengumuman
   POST /broadcasts
   {
     "title": "Pertemuan RT",
     "content": "Ada pertemuan RT hari Jumat",
     "broadcast_type": "announcements",
     "expires_at": "2025-01-31T23:59:59"
   }

2. Sistem:
   ├─ Create broadcast
   ├─ Create activity_log
   └─ Push notif ke semua warga

3. Warga melihat di dashboard
   GET /broadcasts
```

### 4.2 Kegiatan

**Tabel: activities**
```sql
id              INT PRIMARY KEY
title           VARCHAR
description     TEXT
activity_date   DATE
activity_time   TIME
location        VARCHAR
created_by      INT (FK to users - RT)
status          ENUM: planned, ongoing, completed, cancelled
```

**Flow:**
```
1. RT buat kegiatan
   POST /activities
   {
     "title": "Kerja bakti",
     "description": "Bersih-bersih lingkungan",
     "activity_date": "2025-01-15",
     "activity_time": "08:00:00",
     "location": "Sekitar RT 01"
   }

2. Warga lihat jadwal
   GET /activities
```

---

## 5. SISTEM KEUANGAN

### 5.1 Iuran Warga (income_bills)

**Tabel: income_categories**
```sql
id              INT PRIMARY KEY
name            VARCHAR (e.g., "Sampah", "Ronda", "Dana Sosial")
amount          DECIMAL
frequency       ENUM: monthly, yearly, one-time
created_by      INT (FK to users - Bendahara)
created_at      TIMESTAMP
```

**Tabel: income_bills**
```sql
id              INT PRIMARY KEY
resident_id     INT (FK to residents)
category_id     INT (FK to income_categories)
amount          DECIMAL
month           INT (1-12)
year            INT
status          ENUM: unpaid, paid, overdue
due_date        DATE
paid_date       DATE (nullable)
payment_method  VARCHAR (cash, transfer)
verified_by     INT (FK to users - Bendahara, nullable)
verified_at     TIMESTAMP (nullable)
```

**Flow Iuran:**
```
1. Bendahara setup kategori iuran
   POST /income-categories
   {
     "name": "Sampah",
     "amount": 20000,
     "frequency": "monthly"
   }

2. Bendahara buat tagihan bulanan
   POST /income-bills
   {
     "resident_id": 10,
     "category_id": 1,
     "month": 1,
     "year": 2025,
     "due_date": "2025-01-10"
   }
   
   Sistem:
   ├─ status = unpaid
   ├─ Create activity_log
   └─ Notif ke warga: tagihan baru

3. Warga lihat tagihan
   GET /income-bills?status=unpaid

4. Warga bayar (manual cash)
   Bendahara update:
   PUT /income-bills/{id}
   {
     "status": "paid",
     "payment_method": "cash",
     "paid_date": "2025-01-05"
   }
   
   Sistem trigger:
   ├─ Create incomes record (dari income_bills)
   ├─ Create activity_log
   └─ Notif ke warga: pembayaran tercatat

5. Warga bayar (via transfer)
   Warga transfer ke rekening → Bendahara verifikasi
   
   Bendahara:
   PUT /income-bills/{id}
   {
     "status": "paid",
     "payment_method": "transfer",
     "paid_date": "2025-01-05",
     "verified_by": <user_id>,
     "verified_at": "2025-01-05T10:00:00"
   }
```

### 5.2 Pendapatan Lain (income_other)

**Tabel: income_other**
```sql
id              INT PRIMARY KEY
title           VARCHAR
description     TEXT
amount          DECIMAL
source          VARCHAR (donasi, sponsor, sumbangan)
created_by      INT (FK to users - Bendahara)
created_at      TIMESTAMP
```

**Flow:**
```
Bendahara input donasi
POST /income-other
{
  "title": "Donasi acara",
  "description": "Dari PT ABC",
  "amount": 500000,
  "source": "sponsor"
}

Sistem:
├─ Create income_other
├─ Auto create incomes (aggregate record)
├─ Create activity_log
└─ Notif ke RT/RW: ada donasi
```

### 5.3 Pengeluaran RT (spendings)

**Tabel: spendings**
```sql
id              INT PRIMARY KEY
title           VARCHAR
description     TEXT
amount          DECIMAL
category        VARCHAR
created_by      INT (FK to users - Bendahara/RT)
proof_image     VARCHAR (path/url)
proof_file      VARCHAR (path/url - invoice/nota)
status          ENUM: submitted, verified, rejected
verified_by     INT (FK to users - Admin/RT, nullable)
verified_at     TIMESTAMP (nullable)
created_at      TIMESTAMP
```

**Flow Pengeluaran:**
```
1. Bendahara input pengeluaran
   POST /spendings
   {
     "title": "Pembelian cat untuk tembok",
     "description": "Cat untuk pengecatan dinding RT",
     "amount": 150000,
     "category": "perbaikan",
     "proof_image": <file>,
     "proof_file": <file>
   }
   
   Sistem:
   ├─ status = submitted
   ├─ Create activity_log
   └─ Notif ke RT/Admin: ada pengeluaran baru

2. Admin/RT verifikasi
   PUT /spendings/{id}
   {
     "status": "verified"
   }
   
   Sistem:
   ├─ status = verified
   ├─ Auto create incomes deduction (negative)
   ├─ Create activity_log
   └─ Notif ke Bendahara

3. Laporan keuangan bulanan
   GET /financial-reports?month=1&year=2025
   
   Response:
   {
     "period": "Jan 2025",
     "income": 5000000,
     "spending": 1500000,
     "balance": 3500000,
     "details": {...}
   }
```

---

## 6. MARKETPLACE

### 6.1 Verifikasi Sayur (ML Prediction)

**Tabel: verification_results**
```sql
id              INT PRIMARY KEY
resident_id     INT (FK to residents)
image_path      VARCHAR
prediction      ENUM: utuh, tidak_utuh
confidence      DECIMAL (0-1)
is_valid_for_marketplace BOOLEAN
created_at      TIMESTAMP
```

**Flow Verifikasi:**
```
1. Warga upload sayur untuk dicek
   POST /verify-vegetable
   {
     "image": <file>
   }
   
   Sistem:
   ├─ Simpan image → verification_results
   ├─ Kirim ke model ML (PCVK)
   └─ Tunggu hasil

2. Model PCVK return hasil
   ├─ prediction: "utuh" atau "tidak_utuh"
   └─ confidence: 0-1

3. Update verification_results
   ├─ is_valid_for_marketplace = true (jika utuh)
   ├─ is_valid_for_marketplace = false (jika tidak utuh)
   └─ Notif ke warga

4. Jika TIDAK UTUH
   Sistem kirim pesan:
   "Sayur Anda tidak layak dijual (tidak utuh).
    Silakan upload sayur yang utuh."
   
   Warga bisa re-upload

5. Jika UTUH
   Warga bisa lanjut ke marketplace
```

### 6.2 Unggah Produk Marketplace

**Tabel: marketplace_products**
```sql
id              INT PRIMARY KEY
resident_id     INT (FK to residents - seller)
verification_result_id INT (FK to verification_results)
name            VARCHAR
description     TEXT
price           DECIMAL
quantity        INT
unit            VARCHAR (kg, piece, bundle)
image_path      VARCHAR
status          ENUM: active, sold_out, inactive
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**Flow Produk:**
```
1. Warga ambil hasil verifikasi yang VALID
   GET /verification-results?is_valid=true

2. Warga buat produk marketplace
   POST /marketplace-products
   {
     "verification_result_id": 5,
     "name": "Tomat Premium Segar",
     "description": "Tomat organik dari kebun sendiri",
     "price": 50000,
     "quantity": 10,
     "unit": "kg"
   }
   
   Sistem:
   ├─ status = active
   ├─ Create activity_log
   └─ Notif semua: ada produk baru

3. Produk tampil di marketplace
   GET /marketplace-products?status=active
```

### 6.3 Pembelian Produk

**Tabel: marketplace_orders**
```sql
id              INT PRIMARY KEY
product_id      INT (FK to marketplace_products)
buyer_id        INT (FK to users - pembeli)
seller_id       INT (FK to users - penjual, FK to residents)
quantity        INT
total_price     DECIMAL
payment_method  ENUM: cash, transfer
status          ENUM: pending, paid, delivered, cancelled
created_at      TIMESTAMP
paid_at         TIMESTAMP (nullable)
delivered_at    TIMESTAMP (nullable)
```

**Flow Pembelian:**
```
1. Warga (buyer) lihat produk
   GET /marketplace-products/{id}

2. Warga buat order
   POST /marketplace-orders
   {
     "product_id": 5,
     "quantity": 2,
     "payment_method": "transfer"
   }
   
   Sistem:
   ├─ status = pending
   ├─ total_price = quantity * price
   ├─ Create activity_log
   └─ Notif penjual: ada order baru

3. Pembeli bayar
   Update order:
   PUT /marketplace-orders/{id}
   {
     "status": "paid",
     "paid_at": "2025-01-10T10:00:00"
   }

4. Penjual konfirmasi & kirim
   PUT /marketplace-orders/{id}
   {
     "status": "delivered",
     "delivered_at": "2025-01-10T15:00:00"
   }
   
   Sistem:
   ├─ Update marketplace_products.quantity
   ├─ Create activity_log
   └─ Notif pembeli: sudah dikirim

5. Pembatalan
   PUT /marketplace-orders/{id}
   {
     "status": "cancelled"
   }
   
   Jika belum bayar: cancel normal
   Jika sudah bayar: refund ke pembeli
```

---

## 7. ACTIVITY LOGS

**Tabel: activity_logs**
```sql
id              INT PRIMARY KEY
action          VARCHAR (e.g., "approve_warga", "create_iuran", "bayar_iuran")
actor_id        INT (FK to users - siapa yang action)
target_id       INT (FK ke tabel berbeda sesuai action)
target_type     VARCHAR (e.g., "resident", "income_bill", "product")
description     TEXT
created_at      TIMESTAMP
```

**Recorded Actions:**
```
approve_warga              → resident approval
reject_warga               → resident rejection
create_resident            → new resident added
create_iuran               → billing created
bayar_iuran                → payment recorded
create_pengeluaran         → spending added
verify_pengeluaran         → spending verified
create_broadcast           → announcement posted
create_kegiatan            → activity created
verify_sayur               → vegetable verified
create_produk_marketplace  → product uploaded
buat_order                 → purchase order created
pembayaran_order           → order paid
pengiriman_order           → order delivered
cancel_order               → order cancelled
```

---

## 10. AUTHORIZATION & ROLE-BASED ACCESS

### Key Authorization Rules

```
WARGA TIDAK BISA:
❌ Menambah anggota keluarga sendiri
❌ Ubah status keluarga sendiri
❌ Ubah family_id sendiri
❌ Access data keluarga orang lain

HANYA BISA:
✓ Register sendiri (self-registration)
✓ Login dengan akun mereka
✓ Lihat data keluarga mereka sendiri
✓ Ajukan mutasi (pindah/meninggal)
✓ Kirim pesan ke RT/RW
✓ Lihat iuran mereka
✓ Upload & jual di marketplace

ADMIN/RT BISA:
✓ Input residents baru + family
✓ Assign residents ke family
✓ Approve/reject self-registration
✓ Assign family_id saat approval
✓ Create/update family data
✓ Handle mutasi keluarga
✓ Manage semua data kependudukan
```

### Endpoint Access Control

```
┌─────────────────────────┬──────────┬────────┬────────┬──────────┬────────┬────────┐
│ Endpoint                │  Admin   │  RW    │  RT    │ Sekretn. │Bendahr │ Warga  │
├─────────────────────────┼──────────┼────────┼────────┼──────────┼────────┼────────┤
│ /residents              │   CRU*   │   R*   │  CRU*  │    R     │   R    │   R    │
│ /resident-approvals     │   CRU    │   RU   │  RU    │    R     │   -    │   -    │
│ /family-mutations       │   CRU    │   RU   │  CRU   │    R     │   -    │   -    │
│ /resident-messages      │   R      │   RU   │  RU    │    R     │   -    │   CR   │
│ /broadcasts             │   CRU    │   CRU  │  CRU   │    -     │   -    │   R    │
│ /activities             │   CRU    │   RU   │  CRU   │    R     │   -    │   R    │
│ /income-categories      │   CRU    │   R    │   R    │    R     │  CRU   │   R    │
│ /income-bills           │   CRU    │   R    │   R    │    R     │  CRU   │   R*   │
│ /income-other           │   CRU    │   R    │   R    │    -     │  CR    │   -    │
│ /spendings              │   CRU    │   RU   │   R    │    -     │  CR    │   -    │
│ /verify-vegetable       │   CR     │   -    │   -    │    -     │   -    │  CR    │
│ /marketplace-products   │   CRU    │   -    │   -    │    -     │   -    │ CRU*   │
│ /marketplace-orders     │   CRU    │   -    │   -    │    -     │   -    │ CRU*   │
│ /financial-reports      │   R      │   R    │   R    │    R     │  R     │   -    │
└─────────────────────────┴──────────┴────────┴────────┴──────────┴────────┴────────┘

Legend:
C = Create        R = Read       U = Update       D = Delete
* = Partial access (e.g., R* = read own data only)
- = No access
```

### Role Permissions Matrix

```javascript
const ROLES = {
  admin: {
    description: "Akses penuh sistem",
    permissions: ["all"]
  },
  ketua_rw: {
    description: "Supervisi RW & verifikasi RT",
    permissions: [
      "read:residents",
      "read:resident-approvals",
      "update:resident-approvals",
      "read:family-mutations",
      "update:family-mutations",
      "read:broadcasts",
      "create:broadcasts",
      "update:broadcasts",
      "read:activities",
      "read:income-categories",
      "read:income-bills",
      "read:spendings",
      "update:spendings",
      "read:financial-reports"
    ]
  },
  ketua_rt: {
    description: "Supervisi RT & input data",
    permissions: [
      "create:residents",
      "read:residents",
      "update:residents",
      "delete:residents",
      "read:resident-approvals",
      "update:resident-approvals",
      "create:family-mutations",
      "read:family-mutations",
      "update:family-mutations",
      "create:resident-messages",
      "read:resident-messages",
      "update:resident-messages",
      "create:broadcasts",
      "read:broadcasts",
      "update:broadcasts",
      "create:activities",
      "read:activities",
      "update:activities",
      "read:income-categories",
      "read:income-bills",
      "read:spendings",
      "read:financial-reports"
    ]
  },
  sekretaris: {
    description: "Input data & dokumentasi",
    permissions: [
      "read:residents",
      "read:resident-approvals",
      "read:family-mutations",
      "create:resident-messages",
      "read:resident-messages",
      "read:broadcasts",
      "read:activities",
      "read:income-categories",
      "read:income-bills",
      "read:financial-reports"
    ]
  },
  bendahara: {
    description: "Manage keuangan RT",
    permissions: [
      "read:residents",
      "read:income-categories",
      "create:income-categories",
      "read:income-bills",
      "create:income-bills",
      "update:income-bills",
      "create:income-other",
      "create:spendings",
      "read:spendings",
      "read:financial-reports"
    ]
  },
  warga: {
    description: "User biasa",
    permissions: [
      "read:residents:self",
      "read:resident-messages:self",
      "create:resident-messages",
      "update:resident-messages:self",
      "read:broadcasts",
      "read:activities",
      "read:income-bills:self",
      "create:verify-vegetable",
      "read:verify-vegetable:self",
      "create:marketplace-products",
      "read:marketplace-products",
      "update:marketplace-products:self",
      "delete:marketplace-products:self",
      "create:marketplace-orders",
      "read:marketplace-orders:self",
      "update:marketplace-orders:self"
    ]
  }
}
```

---

## 11. NOTES IMPLEMENTASI

```
POST   /auth/login              → Login user
POST   /auth/register           → Self-registration (pending approval)
GET    /auth/me                 → Get current user profile
POST   /auth/refresh            → Refresh access token
POST   /auth/logout             → Logout (client-side)

Token Type: Bearer JWT
Expires: 30 minutes
```

### Example Usage Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {...}
}

# 2. Use token untuk request
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <access_token>"

# 3. Refresh token jika akan expire
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer <access_token>"

# 4. Logout (client-side delete token)
```

---

## 10. NOTES IMPLEMENTASI

### Hal yang sudah siap:
✅ Auth login/register/me/refresh/logout endpoints
✅ Role-based access control middleware
✅ Token generation & validation (30 min expiry)
✅ Password hashing (SHA256)
✅ User model & schema

### Hal yang perlu dikembangkan:
⏳ Resident approvals endpoints
⏳ Family mutations endpoints
⏳ Income/spending management endpoints
⏳ Marketplace endpoints
⏳ Verification vegetable (ML integration)
⏳ Broadcast & activities endpoints
⏳ Activity logs endpoints
⏳ Financial reports endpoints
⏳ Push notification system

### Database Seeding:
✅ Users dengan 6 roles sudah di-seed
✅ Sample residents sudah di-seed
✅ Income categories sudah ada
✅ Test data siap untuk development

### Testing:
✅ Swagger UI: http://localhost:8000/docs
✅ Postman collection: POSTMAN_COLLECTION.json
✅ Credentials: admin/admin123, warga/password123
