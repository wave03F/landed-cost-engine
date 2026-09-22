# Use Case Specification — Landed Cost Engine

> เอกสารนี้สรุป Use Case ทั้งหมดของระบบ **Cross-Border Trade Compliance & Landed-Cost Engine**
> วิเคราะห์จากโค้ดจริง (FastAPI routers/services + Next.js routes) ไม่ใช่การสมมติ
> ใช้อ้างอิงร่วมกันได้ระหว่างทีม Dev / QA / Business
>
> **เวอร์ชัน:** 3.1 · **วันที่วิเคราะห์:** 22 ก.ย. 2026 · **ผู้จัดทำ:** System Analysis
>
> **หมายเหตุเวอร์ชัน 3.1:** สะท้อนการแก้ไขล่าสุดครบทุกประเด็น — บังคับสิทธิ์ Admin, โควตาต่อวัน,
> ประวัติ per-user, CRUD ครบทุก entity (รวม FX delete), endpoint จัดการสิทธิ์ผู้ใช้ (promote/demote),
> referential guard กันลบ HTS ที่ยังมีกฎอ้างถึง, และ **soft-close** สำหรับกฎภาษี/exclusion เชิง compliance

---

## สารบัญ

1. [ภาพรวมระบบ (System Context)](#1-ภาพรวมระบบ)
2. [A. Actors — ผู้เกี่ยวข้องกับระบบ](#a-actors--ผู้เกี่ยวข้องกับระบบ)
3. [B. รายการ Use Case ทั้งหมด (จัดกลุ่มตาม Module)](#b-รายการ-use-case-ทั้งหมด)
4. [C. รายละเอียด Use Case แต่ละอัน](#c-รายละเอียด-use-case-แต่ละอัน)
5. [D. Use Case Diagram (อธิบายเป็นข้อความ)](#d-use-case-diagram-อธิบายเป็นข้อความ)
6. [E. ตาราง Summary](#e-ตาราง-summary-ของ-use-case-ทั้งหมด)
7. [F. ข้อสังเกต / Roadmap / ต้องถาม Stakeholder](#f-ข้อสังเกต--roadmap--ต้องถาม-stakeholder)

---

## 1. ภาพรวมระบบ

ระบบนี้ช่วยผู้นำเข้าสินค้าจากจีนมายังสหรัฐฯ คำนวณ **"ต้นทุนนำเข้ารวมที่แท้จริง" (Landed Cost)**
โดยรวมภาษีศุลกากรหลายชั้นเข้าด้วยกันอย่างถูกต้อง (MFN + Section 301 + Section 232 + IEEPA)
พร้อมจัดการกฎการซ้อนภาษี (stacking) และภาษีที่ใช้แทนกัน (mutual exclusion) การแปลงสกุลเงิน
และการเก็บบันทึกเพื่อตรวจสอบย้อนหลัง (audit trail)

พูดง่ายๆ คือ แทนที่ทีมจัดซื้อจะเปิด Excel ไล่หาอัตราภาษีทีละตัว 15–20 นาที และมีโอกาสผิดสูง
ระบบจะตอบให้ภายในเสี้ยววินาที พร้อมแสดงว่าใช้กฎอะไรบ้าง ตัดกฎไหนออก และเพราะอะไร

---

## A. Actors — ผู้เกี่ยวข้องกับระบบ

| Actor | คือใคร | ทำอะไรได้ในระบบ |
|-------|--------|------------------|
| **Guest (ผู้เยี่ยมชม)** | ผู้ที่ยังไม่ได้ล็อกอิน | เข้าหน้า Login, เริ่มขั้นตอน OAuth |
| **Registered User (ผู้ใช้ทั่วไป)** | ผู้ใช้ที่ล็อกอินผ่าน Google/GitHub แล้ว (role = `user`) | คำนวณ Landed Cost (ภายในโควตาต่อวัน), ค้นหา/ดู HTS, ดูกฎภาษี/ข้อยกเว้น/FX, ดูประวัติการคำนวณ **ของตนเอง**, บันทึก HTS โปรด, เปรียบเทียบ, พิมพ์/ส่งออก PDF |
| **Admin (ผู้ดูแลระบบ)** | ผู้ใช้ที่มี role = `admin` | ทำได้ทุกอย่างเหมือน User และ **จัดการข้อมูลอ้างอิงแบบ CRUD** (กฎภาษี, ข้อยกเว้น, FX, HTS), **จัดการผู้ใช้** (ดูรายชื่อ, เปลี่ยน role), ดูประวัติการคำนวณ **ของทุกคน**, มีโควตาการคำนวณต่อวันสูงมาก |
| **API Client / Service (ระบบภายนอก)** | ระบบอื่นที่เรียกผ่าน `X-API-Key` ที่ถูกต้อง | เรียก endpoint การคำนวณและข้อมูลอ้างอิงแบบ machine-to-machine; ถูกปฏิบัติเป็น **trusted service** (ผ่านด่าน admin ได้), เห็นประวัติทั้งหมด, ไม่ผูกโควตา |
| **OAuth Provider (Google / GitHub)** | ระบบยืนยันตัวตนภายนอก | รับรองตัวตนผู้ใช้ และส่ง profile กลับมาให้ระบบออก JWT |
| **FX Rate Source (แหล่งอัตราแลกเปลี่ยน)** | ฐานข้อมูล FX ภายใน (มี fallback หา rate วันที่ใกล้เคียง) | ให้อัตราแลกเปลี่ยน CNY→USD ตามวันที่นำเข้า |

> **การแบ่งสิทธิ์ (บังคับใช้จริงแล้วในโค้ด):**
> - Endpoint แบบ read (ดู HTS, กฎภาษี, exclusions, FX, ประวัติ) ใช้ตัวตรวจ `require_api_key` — user ทั่วไป, admin, หรือ API Key ก็เข้าได้
> - Endpoint แบบ write ที่จัดการข้อมูลอ้างอิง (create/update/delete ของ HTS, tariff rules, exclusions, FX) ใช้ `require_admin`
>   ซึ่งผ่านได้เฉพาะ **JWT ที่ role = admin**, **API Key ที่ถูกต้อง** (ถือเป็น trusted service), หรือ **dev mode** (ไม่ได้ตั้งค่า key ใดเลย)
> - ผู้ใช้ทั่วไปเรียก write endpoint เหล่านี้จะได้ **HTTP 403**

---

## B. รายการ Use Case ทั้งหมด

### Module 1: Authentication & Account (การยืนยันตัวตน)
- **UC-001** เข้าสู่ระบบด้วย Google/GitHub (OAuth Login)
- **UC-002** ต่ออายุ Access Token (Refresh Token)
- **UC-003** ดูโปรไฟล์ผู้ใช้ปัจจุบัน
- **UC-004** ออกจากระบบ (Logout)

### Module 2: Landed Cost Calculation (การคำนวณต้นทุนนำเข้า) — Core
- **UC-010** คำนวณต้นทุนนำเข้ารวม (Calculate Landed Cost) — บังคับโควตาต่อวัน + ผูกกับผู้ใช้

### Module 3: HTS Code Management (การจัดการรหัสพิกัดศุลกากร)
- **UC-020** ค้นหารหัส HTS
- **UC-021** ดูรายละเอียดรหัส HTS
- **UC-022** เพิ่มรหัส HTS ใหม่ *(admin)*
- **UC-023** แก้ไขรหัส HTS *(admin)* — **ใหม่**
- **UC-024** ลบรหัส HTS *(admin)* — **ใหม่**

### Module 4: Tariff Rules & Exclusions (กฎภาษีและข้อยกเว้น)
- **UC-030** ดูรายการกฎภาษี
- **UC-031** สร้างกฎภาษีใหม่ *(admin)*
- **UC-032** แก้ไขกฎภาษี *(admin)*
- **UC-033** ลบกฎภาษี *(admin)* — hard delete เฉพาะกฎที่ยังไม่มีผล
- **UC-038** ปิดกฎภาษี (soft-close) *(admin)* — **ใหม่**
- **UC-034** ดูรายการข้อยกเว้นภาษี
- **UC-035** สร้างข้อยกเว้นภาษีใหม่ *(admin)*
- **UC-036** แก้ไขข้อยกเว้นภาษี *(admin)*
- **UC-037** ลบข้อยกเว้นภาษี *(admin)* — hard delete เฉพาะที่ยังไม่มีผล
- **UC-039** ปิดข้อยกเว้นภาษี (soft-close) *(admin)* — **ใหม่**

### Module 5: FX Rates (อัตราแลกเปลี่ยน)
- **UC-040** ดูอัตราแลกเปลี่ยนย้อนหลัง
- **UC-041** เพิ่ม/อัปเดตอัตราแลกเปลี่ยน *(admin)*
- **UC-042** ลบอัตราแลกเปลี่ยน *(admin)* — **ใหม่**

### Module 6: Audit Trail (ประวัติการคำนวณ)
- **UC-050** ดูประวัติการคำนวณย้อนหลัง (per-user / admin เห็นทั้งหมด)
- **UC-051** ดูรายละเอียดการคำนวณครั้งเดียว (ตรวจ ownership)

### Module 7: Favorites (รายการโปรด)
- **UC-060** บันทึก HTS code เป็นรายการโปรด
- **UC-061** ดู HTS code ที่บันทึกไว้
- **UC-062** ลบ HTS code ออกจากรายการโปรด

### Module 8: Comparison & Export (เปรียบเทียบและส่งออก) — Frontend
- **UC-070** เปรียบเทียบผลการคำนวณหลายกรณี
- **UC-071** พิมพ์ / ส่งออกผลลัพธ์เป็น PDF

### Module 9: User Management (การจัดการผู้ใช้) — ใหม่
- **UC-080** ดูรายชื่อผู้ใช้ทั้งหมด *(admin)* — **ใหม่**
- **UC-081** ดูข้อมูลผู้ใช้รายคน *(admin)* — **ใหม่**
- **UC-082** เปลี่ยน role ผู้ใช้ (promote/demote admin) *(admin)* — **ใหม่**

---

## C. รายละเอียด Use Case แต่ละอัน

---

### UC-001 — เข้าสู่ระบบด้วย Google/GitHub (OAuth Login)

- **Use Case ID:** UC-001
- **Actor:** Guest, OAuth Provider (Google/GitHub)
- **Description:** ผู้ใช้เข้าสู่ระบบผ่านผู้ให้บริการ OAuth ระบบสร้าง/ค้นหาบัญชีผู้ใช้ แล้วออก JWT (access + refresh token)
- **Preconditions:**
  - ผู้ใช้ยังไม่ได้ล็อกอิน
  - ระบบตั้งค่า OAuth client ของ Google/GitHub ไว้เรียบร้อย
- **Main Flow:**
  1. Guest กดปุ่ม "Login with Google" (หรือ GitHub) ที่หน้า Login
  2. ระบบ redirect ไปยังหน้า consent ของ OAuth Provider (`GET /auth/login/{provider}`)
  3. ผู้ใช้อนุญาตสิทธิ์กับ Provider
  4. Provider ส่ง `code` กลับมาที่ callback (`GET /auth/callback/{provider}`)
  5. ระบบแลก `code` เป็น access token ของ Provider และดึง profile
  6. ระบบค้นหาผู้ใช้จาก email/oauth_id ถ้าไม่มีให้สร้างใหม่ (role เริ่มต้น = `user`)
  7. ระบบออก JWT access token + refresh token
  8. ระบบ redirect กลับไปที่หน้า frontend `/auth/success?access_token=...&refresh_token=...`
  9. Frontend เก็บ token และพาผู้ใช้เข้าสู่ระบบ
- **Alternative Flow:**
  - 6a. ถ้าผู้ใช้เคยสมัครแล้ว ระบบใช้บัญชีเดิม (ไม่สร้างซ้ำ)
- **Exception Flow:**
  - 3a. ผู้ใช้ปฏิเสธสิทธิ์ที่ Provider → ไม่มี `code` ส่งกลับ, ผู้ใช้ยังคงเป็น Guest
  - 5a. แลก `code` ไม่สำเร็จ / profile ไม่ถูกต้อง → ระบบตอบ **HTTP 400** `OAuth failed: ...`
- **Postconditions:** ผู้ใช้มีบัญชีในระบบและถือ JWT ที่ใช้เรียก API ที่ต้องยืนยันตัวตนได้
- **Business Rules:**
  - ไม่มีการเก็บรหัสผ่าน — มอบหมายการยืนยันตัวตนให้ OAuth Provider ทั้งหมด
  - email ต้องไม่ซ้ำ (unique) ในระบบ
  - role ของผู้ใช้ใหม่เป็น `user` เสมอ (การเลื่อนเป็น admin ทำที่ระดับฐานข้อมูล — ดู F)

---

### UC-002 — ต่ออายุ Access Token (Refresh Token)

- **Use Case ID:** UC-002
- **Actor:** Registered User / API Client
- **Description:** แลก refresh token ที่ยังไม่หมดอายุเป็น access token ใหม่ โดยไม่ต้องล็อกอินซ้ำ
- **Preconditions:** ผู้ใช้เคยล็อกอินและมี refresh token ที่ยังไม่หมดอายุ
- **Main Flow:**
  1. Client ส่ง `POST /auth/refresh` พร้อม refresh token
  2. ระบบตรวจสอบความถูกต้องของ refresh token
  3. ระบบดึงข้อมูลผู้ใช้เพื่ออ่าน role ปัจจุบัน
  4. ระบบออก access token ใหม่ (ฝัง role ปัจจุบัน) และส่งกลับ
- **Alternative Flow:** —
- **Exception Flow:**
  - 2a. refresh token ไม่ถูกต้อง/หมดอายุ → **HTTP 401** `Invalid or expired refresh token`
  - 3a. ไม่พบผู้ใช้ในระบบ → **HTTP 401** `User not found`
- **Postconditions:** Client ได้ access token ใหม่ (อายุ 15 นาที)
- **Business Rules:** JWT เป็นแบบ stateless (ไม่มีการเก็บ session ฝั่ง server); access token อายุ 15 นาที, refresh token อายุ 7 วัน

---

### UC-003 — ดูโปรไฟล์ผู้ใช้ปัจจุบัน

- **Use Case ID:** UC-003
- **Actor:** Registered User
- **Description:** ดูข้อมูลโปรไฟล์ของผู้ใช้ที่ล็อกอินอยู่
- **Preconditions:** ผู้ใช้ล็อกอินแล้ว (มี Bearer token ที่ถูกต้อง)
- **Main Flow:**
  1. Client ส่ง `GET /auth/me` พร้อม Bearer token
  2. ระบบตรวจสอบ token และดึงข้อมูลผู้ใช้
  3. ระบบคืน id, email, name, avatar_url, role, created_at
- **Exception Flow:**
  - 2a. token ไม่ถูกต้อง/ไม่มี → **HTTP 401** `Not authenticated`
- **Postconditions:** ไม่มีการเปลี่ยนสถานะระบบ (read-only)
- **Business Rules:** —

---

### UC-004 — ออกจากระบบ (Logout)

- **Use Case ID:** UC-004
- **Actor:** Registered User
- **Description:** ผู้ใช้ออกจากระบบ (ฝั่ง client ทิ้ง token)
- **Preconditions:** ผู้ใช้ล็อกอินอยู่
- **Main Flow:**
  1. ผู้ใช้กด Logout
  2. Client เรียก `POST /auth/logout`
  3. ระบบตอบยืนยัน (ไม่มี state ฝั่ง server ให้เคลียร์)
  4. Client ลบ access/refresh token ที่เก็บไว้
- **Exception Flow:** —
- **Postconditions:** Client ไม่มี token อีกต่อไป ผู้ใช้กลับเป็น Guest
- **Business Rules:** เนื่องจาก JWT เป็น stateless ระบบไม่มีการ invalidate token ฝั่ง server (token ยังมีผลจนหมดอายุ)

---

### UC-010 — คำนวณต้นทุนนำเข้ารวม (Calculate Landed Cost) ⭐ Core

- **Use Case ID:** UC-010
- **Actor:** Registered User / API Client
- **Description:** คำนวณต้นทุนนำเข้ารวมของสินค้า 1 รายการ โดยรวมภาษีทุกชั้น ค่าธรรมเนียม การแปลงสกุลเงิน บังคับโควตาต่อวัน และบันทึก audit ที่ผูกกับผู้ใช้
- **Preconditions:**
  - ผู้เรียกผ่านการยืนยันตัวตน (JWT หรือ API Key; ใน dev mode ปิด auth)
  - รหัส HTS ที่ระบุมีอยู่ในระบบ
  - (กรณีผู้ใช้ล็อกอิน) ยังใช้โควตาการคำนวณของวันนั้นไม่ครบ
- **Main Flow:**
  1. Client ส่ง `POST /calculate` พร้อม hts_code, มูลค่าสินค้า (CNY หรือ USD), origin_country, import_date, freight, insurance
  2. **[ใหม่] ระบบตรวจโควตาต่อวัน** (เฉพาะผู้ใช้ล็อกอิน): ถ้าวันเปลี่ยนให้รีเซ็ตตัวนับ, ถ้ายังไม่ถึง limit ให้ +1
  3. ระบบตรวจสอบว่ารหัส HTS มีอยู่จริง
  4. ถ้าส่งมาเป็น CNY ระบบแปลงเป็น USD ด้วยอัตราแลกเปลี่ยน ณ วันที่นำเข้า (มี fallback หา rate วันที่ใกล้เคียง)
  5. ระบบรวมมูลค่า = สินค้า + ค่าขนส่ง + ประกัน
  6. ระบบตรวจ De minimis: ถ้ามูลค่ารวม ≤ $800 → ไม่มีภาษีและค่าธรรมเนียม (จบด้วย Alternative Flow A1)
  7. ระบบคำนวณ Customs Value (CIF)
  8. ระบบตรวจ FTA: ถ้า origin เป็น MX/CA (USMCA) จะยกเว้น MFN
  9. Rule Engine ดึงกฎภาษีที่มีผล ณ วันที่นำเข้า (จับคู่แบบลำดับชั้นของ HTS + ช่วงวันที่)
  10. ระบบตรวจ Exclusion และตัดชนิดภาษีที่ถูกยกเว้นออก
  11. ระบบใช้ Stacking Logic: MFN เป็นฐาน, ภาษีที่ stack ได้จะซ้อนขึ้นบน, กลุ่มที่ mutually exclusive เก็บเฉพาะเรตสูงสุด
  12. ระบบคำนวณค่าธรรมเนียม MPF และ HMF
  13. ระบบรวมเป็น Landed Cost และ **บันทึก audit log พร้อม calculation_id และ user_id** (null ถ้าเป็น API Key/dev)
  14. ระบบคืน breakdown ทุกชั้นภาษี (รวมชั้นที่ถูกตัดออกพร้อมเหตุผล), exclusions ที่ใช้, และ FX ที่ใช้
- **Alternative Flow:**
  - **A1 (De minimis):** ที่ขั้นตอน 6 ถ้ามูลค่า ≤ $800 → คืนผลโดย total_duty = 0, ไม่มีค่าธรรมเนียม, `de_minimis_applied = true`, ยังคงบันทึก audit
  - **A2 (FTA):** ที่ขั้นตอน 8 ถ้าเป็น USMCA → MFN แสดงในผลลัพธ์แต่ `applied = false` เหตุผล `exempt_under_USMCA`
  - **A3 (Mutual exclusion):** ที่ขั้นตอน 11 เช่น Section 301 (25%) กับ IEEPA (14.5%) จะเก็บ 301 และตัด IEEPA เหตุผล `excluded_by_stacking_rule`
- **Exception Flow:**
  - **2a. [ใหม่] โควตาต่อวันเต็ม** (ผู้ใช้ล็อกอิน) → **HTTP 429** `Daily calculation limit reached (...)` และไม่ทำการคำนวณ
  - 3a. รหัส HTS ไม่มีในระบบ → **HTTP 400** `HTS code '...' not found`
  - 1a. ไม่ส่งทั้ง invoice_value_cny และ invoice_value_usd → **HTTP 400** `Either invoice_value_cny or invoice_value_usd must be provided`
  - 4a. ไม่มีอัตราแลกเปลี่ยนใกล้เคียงเลย → การแปลงสกุลเงินล้มเหลว (ดู F: ต้องยืนยัน behavior)
- **Postconditions:**
  - มีการบันทึก CalculationLog แบบ immutable ผูกกับ user_id (ผลลัพธ์เดิมจะไม่เปลี่ยนแม้กฎจะแก้/ลบในภายหลัง)
  - (ผู้ใช้ล็อกอิน) ตัวนับ `daily_calculations` ของวันนั้นเพิ่มขึ้น 1
  - Client ได้ผลการคำนวณครบพร้อม calculation_id สำหรับตรวจย้อนหลัง
- **Business Rules:**
  - **BR-1:** MFN เป็นภาษีฐานเสมอ (ถ้ามีกฎ)
  - **BR-2:** ภาษีที่ mutually exclusive กัน จ่ายเฉพาะเรตสูงสุด (ไม่บวกซ้อน)
  - **BR-3:** De minimis ≤ $800 → ยกเว้นภาษีและค่าธรรมเนียม (19 USC 1321)
  - **BR-4:** USMCA (MX/CA) ยกเว้น MFN สำหรับสินค้าที่เข้าเงื่อนไข
  - **BR-5:** MPF = 0.3464% (ขั้นต่ำ $31.67 สูงสุด $614.35), HMF = 0.125% (ไม่มีเพดาน)
  - **BR-6:** กฎที่เฉพาะเจาะจงกว่า (HTS pattern ยาวกว่า) มีลำดับความสำคัญเหนือกฎระดับ chapter/heading
  - **BR-7 [ใหม่]:** โควตาต่อวัน — ผู้ใช้ทั่วไป 50 ครั้ง/วัน, admin 99,999 ครั้ง/วัน (ตั้งค่าได้ผ่าน config); ตัวนับรีเซ็ตเมื่อขึ้นวันใหม่
  - **BR-8 [ใหม่]:** การเรียกด้วย API Key / dev mode ไม่ผูกโควตาและบันทึก user_id = null

---

### UC-020 — ค้นหารหัส HTS

- **Use Case ID:** UC-020
- **Actor:** Registered User / Admin / API Client
- **Description:** ค้นหารหัสพิกัดศุลกากรตาม prefix ของรหัส หรือ keyword ในคำอธิบาย
- **Preconditions:** ผ่านการยืนยันตัวตน
- **Main Flow:**
  1. Client ส่ง `GET /hts-codes?q=...&level=...`
  2. ระบบค้นหาตาม prefix/keyword และ filter ตาม level ถ้าระบุ (chapter/heading/subheading)
  3. ระบบคืนรายการผลลัพธ์ (จำกัด 50 รายการ)
- **Alternative Flow:**
  - 1a. ถ้า `q` ว่าง → คืนรายการทั่วไป (ตามลำดับรหัส)
- **Exception Flow:**
  - 0a. ไม่ผ่านการยืนยันตัวตน → **HTTP 401**
- **Postconditions:** read-only
- **Business Rules:** ผลลัพธ์จำกัดสูงสุด 50 รายการต่อคำค้น

---

### UC-021 — ดูรายละเอียดรหัส HTS

- **Use Case ID:** UC-021
- **Actor:** Registered User / Admin / API Client
- **Description:** ดึงข้อมูลของรหัส HTS ที่ระบุ
- **Preconditions:** ผ่านการยืนยันตัวตน
- **Main Flow:**
  1. Client ส่ง `GET /hts-codes/{code}`
  2. ระบบค้นหาและคืนรายละเอียด
- **Exception Flow:**
  - 2a. ไม่พบรหัส → **HTTP 404**
- **Postconditions:** read-only
- **Business Rules:** —

---

### UC-022 — เพิ่มรหัส HTS ใหม่ *(admin)*

- **Use Case ID:** UC-022
- **Actor:** Admin / API Client (trusted service)
- **Description:** เพิ่มรหัส HTS ใหม่เข้าระบบ ระบบกำหนด level อัตโนมัติจากรูปแบบรหัส
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin (JWT role=admin, API Key ที่ถูกต้อง, หรือ dev mode)
- **Main Flow:**
  1. Client ส่ง `POST /hts-codes` พร้อมข้อมูลรหัสและคำอธิบาย
  2. ระบบตรวจสิทธิ์ admin
  3. ระบบตรวจสอบและกำหนด level อัตโนมัติ
  4. ระบบบันทึกและคืนข้อมูลที่สร้าง (**HTTP 201**)
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป (role=user) → **HTTP 403** `Admin role required`
  - 3a. รหัสซ้ำ → **HTTP 409** `HTS code '...' already exists`
- **Postconditions:** มีรหัส HTS ใหม่ในระบบ ใช้ในการคำนวณได้
- **Business Rules:** level ถูกกำหนดจากความยาว/รูปแบบของรหัส (chapter ≤2, heading ≤4, subheading >4)

---

### UC-023 — แก้ไขรหัส HTS *(admin)* — ใหม่

- **Use Case ID:** UC-023
- **Actor:** Admin / API Client (trusted service)
- **Description:** อัปเดตคำอธิบาย/parent ของรหัส HTS เฉพาะ field ที่ส่งมาจะถูกแก้ไข
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; รหัสนั้นมีอยู่
- **Main Flow:**
  1. Client ส่ง `PUT /hts-codes/{code}` พร้อม field ที่ต้องการแก้ (description, parent_code)
  2. ระบบตรวจสิทธิ์ admin และค้นหารหัส
  3. ระบบอัปเดตเฉพาะ field ที่ส่งมา และคืนผล
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบรหัส → **HTTP 404** `HTS code '...' not found`
- **Postconditions:** ข้อมูลรหัส HTS ถูกปรับปรุง
- **Business Rules:** ไม่อนุญาตให้เปลี่ยน `code` เอง (แก้ได้เฉพาะ description/parent)

---

### UC-024 — ลบรหัส HTS *(admin)* — ใหม่

- **Use Case ID:** UC-024
- **Actor:** Admin / API Client (trusted service)
- **Description:** ลบรหัส HTS ออกจากระบบ
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; รหัสนั้นมีอยู่
- **Main Flow:**
  1. Client ส่ง `DELETE /hts-codes/{code}`
  2. ระบบตรวจสิทธิ์ admin และค้นหารหัส
  3. **[ใหม่] ระบบตรวจ referential guard:** นับกฎภาษี (`tariff_rules.hts_code_pattern`) และ exclusion (`exclusions.hts_code`) ที่อ้างถึงรหัสนี้ (ทั้งรูปแบบมีจุด/ไม่มีจุด)
  4. ถ้าไม่มีการอ้างถึง ระบบลบและตอบ **HTTP 204**
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบรหัส → **HTTP 404**
  - **3a. [ใหม่] มีกฎภาษี/exclusion อ้างถึงอยู่** → **HTTP 409** `Cannot delete HTS code '...': it is still referenced by N tariff rule(s) and M exclusion(s)...` และไม่ลบ
- **Postconditions:** รหัส HTS ถูกลบเมื่อไม่มีการอ้างถึง (การคำนวณเดิมที่บันทึกไว้ไม่กระทบ เพราะ log เก็บผลลัพธ์แบบ immutable)
- **Business Rules:**
  - **[ใหม่]** ต้องลบ/ย้ายกฎภาษีและ exclusion ที่อ้างถึงรหัสก่อน จึงจะลบรหัส HTS ได้ (ป้องกัน dangling reference ใน Rule Engine)

---

### UC-030 — ดูรายการกฎภาษี

- **Use Case ID:** UC-030
- **Actor:** Registered User / Admin / API Client
- **Description:** แสดงกฎภาษีทั้งหมดพร้อม temporal versioning กรองตามชนิดภาษีหรือ HTS ได้
- **Preconditions:** ผ่านการยืนยันตัวตน
- **Main Flow:**
  1. Client ส่ง `GET /tariff-rules?tariff_type=...&hts_code=...`
  2. ระบบคืนรายการกฎที่ตรงเงื่อนไข
- **Exception Flow:** 0a. ไม่ผ่านการยืนยันตัวตน → **HTTP 401**
- **Postconditions:** read-only
- **Business Rules:** ชนิดภาษีที่รองรับ: MFN, SECTION_301, SECTION_232, IEEPA, AD_CVD

---

### UC-031 — สร้างกฎภาษีใหม่ *(admin)*

- **Use Case ID:** UC-031
- **Actor:** Admin / API Client (trusted service)
- **Description:** เพิ่มกฎภาษีใหม่พร้อมตั้งค่า stacking / mutual-exclusion
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin
- **Main Flow:**
  1. Client ส่ง `POST /tariff-rules` พร้อม hts_code_pattern, tariff_type, rate, effective_from/to, stacks_with, mutually_exclusive_with
  2. ระบบตรวจสิทธิ์ admin และ validate ชนิดภาษี
  3. ระบบบันทึกและคืนกฎที่สร้าง (**HTTP 201**)
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. tariff_type ไม่ถูกต้อง → **HTTP 400**; ข้อมูลไม่ผ่าน validation (เช่น rate เกินช่วง 0–5) → **HTTP 422**
- **Postconditions:** กฎใหม่มีผลกับการคำนวณตามช่วงวันที่ที่กำหนด (data-driven ไม่ต้อง deploy)
- **Business Rules:** การเปลี่ยนกฎไม่กระทบผลการคำนวณเดิมที่บันทึกไว้ (immutable audit)

---

### UC-032 — แก้ไขกฎภาษี *(admin)*

- **Use Case ID:** UC-032
- **Actor:** Admin / API Client (trusted service)
- **Description:** อัปเดตกฎภาษีที่มีอยู่ เฉพาะ field ที่ส่งมาจะถูกแก้ไข (partial update)
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; กฎที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `PUT /tariff-rules/{rule_id}` พร้อม field ที่ต้องการแก้
  2. ระบบตรวจสิทธิ์ admin และค้นหากฎ
  3. ระบบอัปเดตเฉพาะ field ที่ส่งมา และคืนกฎที่อัปเดตแล้ว
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ rule_id → **HTTP 404** `Tariff rule '...' not found`
- **Postconditions:** กฎถูกปรับปรุง มีผลกับการคำนวณครั้งถัดไป
- **Business Rules:** แก้ได้เฉพาะ rate, effective_to, stacks_with, mutually_exclusive_with, description, source_reference

---

### UC-033 — ลบกฎภาษี *(admin)*

- **Use Case ID:** UC-033
- **Actor:** Admin / API Client (trusted service)
- **Description:** ลบกฎภาษีออกจากระบบแบบถาวร (hard delete) — อนุญาตเฉพาะกฎที่ยังไม่เคยมีผล
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; กฎที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `DELETE /tariff-rules/{rule_id}`
  2. ระบบตรวจสิทธิ์ admin และค้นหากฎ
  3. **[ใหม่] ระบบตรวจว่ากฎยังไม่มีผล** (`effective_from` อยู่ในอนาคต)
  4. ถ้ายังไม่มีผล ระบบลบและตอบ **HTTP 204**
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ rule_id → **HTTP 404**
  - **3a. [ใหม่] กฎมีผลแล้ว/เคยมีผล** → **HTTP 409** พร้อมข้อความแนะให้ใช้ `POST /tariff-rules/{id}/close` แทน
- **Postconditions:** กฎที่ยังไม่มีผลถูกลบ; การคำนวณเดิมที่บันทึกไว้ไม่กระทบ (log เก็บ rule_id ที่ใช้ ณ เวลาคำนวณ)
- **Business Rules:**
  - **[ใหม่]** hard delete ได้เฉพาะกฎที่ยังไม่เคยมีผล (เช่น ป้อนผิดแล้วจะลบทิ้ง); กฎที่มีผลแล้วต้องใช้ soft-close (UC-038) เพื่อรักษา audit trail

---

### UC-038 — ปิดกฎภาษี (soft-close) *(admin)* — ใหม่

- **Use Case ID:** UC-038
- **Actor:** Admin / API Client (trusted service)
- **Description:** "ปิด" กฎภาษีที่เคยหรือกำลังมีผล โดยตั้งวันสิ้นสุด (`effective_to`) แทนการลบ เพื่อรักษาประวัติเชิง audit
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; กฎที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `POST /tariff-rules/{rule_id}/close` พร้อม `close_date`
  2. ระบบตรวจสิทธิ์ admin และค้นหากฎ
  3. ระบบตั้ง `effective_to = close_date` และคืนกฎที่อัปเดต
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ rule_id → **HTTP 404**
  - 3a. กฎมีวันสิ้นสุดอยู่ก่อนหรือเท่ากับ close_date อยู่แล้ว → **HTTP 400**
- **Postconditions:** กฎยังอยู่ในระบบ (เพื่อ audit) แต่จะไม่ถูกนำไปใช้ในการคำนวณหลัง `close_date`
- **Business Rules:**
  - เป็นวิธี "retire" กฎที่แนะนำ — เก็บกฎไว้ในฐานข้อมูลเพื่อตรวจสอบย้อนหลัง
  - การคำนวณเดิมที่อ้างถึงกฎนี้ไม่กระทบ (log เก็บกฎที่ใช้ ณ เวลาคำนวณ)

---

### UC-034 — ดูรายการข้อยกเว้นภาษี

- **Use Case ID:** UC-034
- **Actor:** Registered User / Admin / API Client
- **Description:** แสดง exclusion ทั้งหมด (ทั้งที่ยังมีผลและหมดอายุ) กรองตาม HTS ได้
- **Preconditions:** ผ่านการยืนยันตัวตน
- **Main Flow:**
  1. Client ส่ง `GET /exclusions?hts_code=...`
  2. ระบบคืนรายการ exclusion
- **Exception Flow:** 0a. ไม่ผ่านการยืนยันตัวตน → **HTTP 401**
- **Postconditions:** read-only
- **Business Rules:** —

---

### UC-035 — สร้างข้อยกเว้นภาษีใหม่ *(admin)*

- **Use Case ID:** UC-035
- **Actor:** Admin / API Client (trusted service)
- **Description:** เพิ่ม exclusion ใหม่ (ยกเว้นภาษีชนิดหนึ่งสำหรับ HTS/ประเทศ ในช่วงเวลาหนึ่ง)
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin
- **Main Flow:**
  1. Client ส่ง `POST /exclusions` พร้อม hts_code, tariff_type, origin_country, effective_from, effective_to (null = ถาวร)
  2. ระบบตรวจสิทธิ์ admin และ validate
  3. ระบบบันทึกและคืน (**HTTP 201**)
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. tariff_type ไม่ถูกต้อง → **HTTP 400**; ข้อมูลไม่ผ่าน validation → **HTTP 422**
- **Postconditions:** exclusion ถูกนำไปใช้อัตโนมัติในการคำนวณที่อยู่ในช่วงวันที่มีผล
- **Business Rules:** ตั้ง `effective_to = null` = ยกเว้นถาวร; exclusion ตัดภาษีชนิดที่ระบุออกจากการคำนวณ

---

### UC-036 — แก้ไขข้อยกเว้นภาษี *(admin)* — ใหม่

- **Use Case ID:** UC-036
- **Actor:** Admin / API Client (trusted service)
- **Description:** อัปเดต exclusion เฉพาะ field ที่ส่งมา (effective_to, description, source_reference)
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; exclusion ที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `PUT /exclusions/{exclusion_id}` พร้อม field ที่ต้องการแก้
  2. ระบบตรวจสิทธิ์ admin และค้นหา exclusion
  3. ระบบอัปเดตและคืนผล
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ exclusion_id → **HTTP 404** `Exclusion '...' not found`
- **Postconditions:** exclusion ถูกปรับปรุง (เช่น ขยาย/ปิดวันหมดอายุ)
- **Business Rules:** ใช้แก้ effective_to เพื่อขยายหรือยุติการยกเว้นได้

---

### UC-037 — ลบข้อยกเว้นภาษี *(admin)*

- **Use Case ID:** UC-037
- **Actor:** Admin / API Client (trusted service)
- **Description:** ลบ exclusion ออกจากระบบแบบถาวร (hard delete) — อนุญาตเฉพาะที่ยังไม่เคยมีผล
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; exclusion ที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `DELETE /exclusions/{exclusion_id}`
  2. ระบบตรวจสิทธิ์ admin และค้นหา exclusion
  3. **[ใหม่] ระบบตรวจว่า exclusion ยังไม่มีผล** (`effective_from` อยู่ในอนาคต)
  4. ถ้ายังไม่มีผล ระบบลบและตอบ **HTTP 204**
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ exclusion_id → **HTTP 404**
  - **3a. [ใหม่] exclusion มีผลแล้ว/เคยมีผล** → **HTTP 409** พร้อมข้อความแนะให้ใช้ `POST /exclusions/{id}/close` แทน
- **Postconditions:** exclusion ที่ยังไม่มีผลถูกลบ
- **Business Rules:** hard delete ได้เฉพาะที่ยังไม่เคยมีผล; ที่มีผลแล้วต้องใช้ soft-close (UC-039)

---

### UC-039 — ปิดข้อยกเว้นภาษี (soft-close) *(admin)* — ใหม่

- **Use Case ID:** UC-039
- **Actor:** Admin / API Client (trusted service)
- **Description:** "ปิด" exclusion ที่เคยหรือกำลังมีผล โดยตั้งวันสิ้นสุด (`effective_to`) แทนการลบ
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; exclusion ที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `POST /exclusions/{exclusion_id}/close` พร้อม `close_date`
  2. ระบบตรวจสิทธิ์ admin และค้นหา exclusion
  3. ระบบตั้ง `effective_to = close_date` และคืน exclusion ที่อัปเดต
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ exclusion_id → **HTTP 404**
  - 3a. exclusion มีวันสิ้นสุดอยู่ก่อนหรือเท่ากับ close_date อยู่แล้ว → **HTTP 400**
- **Postconditions:** exclusion ยังอยู่ในระบบ (เพื่อ audit) แต่จะไม่ถูกนำไปใช้ในการคำนวณหลัง `close_date`
- **Business Rules:** เป็นวิธี "retire" exclusion ที่แนะนำ — เก็บไว้เพื่อตรวจสอบย้อนหลัง

---

### UC-040 — ดูอัตราแลกเปลี่ยนย้อนหลัง

- **Use Case ID:** UC-040
- **Actor:** Registered User / Admin / API Client
- **Description:** แสดงอัตราแลกเปลี่ยนของคู่สกุลเงิน (ค่าเริ่มต้น CNY→USD) กรองตามช่วงวันที่ได้
- **Preconditions:** ผ่านการยืนยันตัวตน
- **Main Flow:**
  1. Client ส่ง `GET /fx-rates?from_currency=CNY&to_currency=USD&date_from=...&date_to=...`
  2. ระบบคืนรายการอัตรา (จำกัด 100 รายการ เรียงวันที่ล่าสุดก่อน)
- **Exception Flow:** 0a. ไม่ผ่านการยืนยันตัวตน → **HTTP 401**
- **Postconditions:** read-only
- **Business Rules:** ผลลัพธ์จำกัด 100 รายการ

---

### UC-041 — เพิ่ม/อัปเดตอัตราแลกเปลี่ยน *(admin)*

- **Use Case ID:** UC-041
- **Actor:** Admin / API Client (trusted service)
- **Description:** เพิ่มอัตราแลกเปลี่ยนสำหรับวันที่ระบุ ถ้ามีอยู่แล้วจะอัปเดต (upsert)
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin
- **Main Flow:**
  1. Client ส่ง `POST /fx-rates` พร้อม from_currency, to_currency, rate, date
  2. ระบบตรวจสิทธิ์ admin แล้วตรวจว่ามีอัตราของวันนั้นอยู่แล้วหรือไม่ → เพิ่มใหม่หรืออัปเดต
  3. ระบบคืนผลลัพธ์ (**HTTP 201**)
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ข้อมูลไม่ผ่าน validation → **HTTP 422**
- **Postconditions:** อัตราแลกเปลี่ยนพร้อมใช้ในการแปลงสกุลเงินของการคำนวณ
- **Business Rules:** 1 อัตราต่อ 1 คู่สกุลเงินต่อ 1 วันที่ (upsert)

---

### UC-042 — ลบอัตราแลกเปลี่ยน *(admin)* — ใหม่

- **Use Case ID:** UC-042
- **Actor:** Admin / API Client (trusted service)
- **Description:** ลบอัตราแลกเปลี่ยนตาม id
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; อัตราที่ระบุมีอยู่
- **Main Flow:**
  1. Client ส่ง `DELETE /fx-rates/{rate_id}`
  2. ระบบตรวจสิทธิ์ admin และค้นหาอัตรา
  3. ระบบลบและตอบ **HTTP 204**
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ rate_id → **HTTP 404** `FX rate '...' not found`
- **Postconditions:** อัตราแลกเปลี่ยนถูกลบ
- **Business Rules:**
  - การลบอัตราที่เคยใช้คำนวณไปแล้วไม่กระทบผลเดิม (log เก็บ fx_rate ที่ใช้ ณ เวลาคำนวณ)
  - หมายเหตุ: ถ้าลบอัตราที่ Rule Engine ต้องใช้ ระบบอาจ fallback ไปอัตราวันใกล้เคียง หรือดึงจาก live API แทน

---

### UC-050 — ดูประวัติการคำนวณย้อนหลัง

- **Use Case ID:** UC-050
- **Actor:** Registered User / Admin / API Client
- **Description:** แสดงรายการการคำนวณ เรียงเวลาล่าสุดก่อน ใช้เป็น audit trail โดยขอบเขตการมองเห็นขึ้นกับ role
- **Preconditions:** ผ่านการยืนยันตัวตน
- **Main Flow:**
  1. Client ส่ง `GET /calculations?hts_code=...&limit=...&offset=...`
  2. **[ใหม่] ระบบกำหนดขอบเขต:** ถ้าเป็นผู้ใช้ทั่วไป (role=user) filter เฉพาะ user_id ของตน; ถ้าเป็น admin หรือ service (API Key/dev) เห็นทั้งหมด
  3. ระบบคืนรายการ (จำกัดสูงสุด 200, มี pagination)
- **Exception Flow:** 0a. ไม่ผ่านการยืนยันตัวตน → **HTTP 401**
- **Postconditions:** read-only
- **Business Rules:**
  - limit ≤ 200; เรียงตาม calculated_at จากใหม่ไปเก่า
  - **[ใหม่]** ผู้ใช้ทั่วไปเห็นเฉพาะประวัติของตนเอง; admin/service เห็นทั้งหมด

---

### UC-051 — ดูรายละเอียดการคำนวณครั้งเดียว

- **Use Case ID:** UC-051
- **Actor:** Registered User / Admin / API Client
- **Description:** ดึงข้อมูลการคำนวณ 1 รายการ ประกอบด้วย input, กฎที่ใช้, exclusions, และผลลัพธ์
- **Preconditions:** ผ่านการยืนยันตัวตน; มี calculation_id
- **Main Flow:**
  1. Client ส่ง `GET /calculations/{calculation_id}`
  2. ระบบค้นหา log
  3. **[ใหม่] ตรวจ ownership:** ถ้าเป็นผู้ใช้ทั่วไปและ log ไม่ใช่ของตน → ถือว่าไม่พบ
  4. ระบบคืนรายละเอียดครบถ้วน
- **Exception Flow:**
  - 2a. ไม่พบ calculation_id → **HTTP 404** `Calculation '...' not found`
  - 3a. **[ใหม่]** ผู้ใช้ทั่วไปเปิดของคนอื่น → **HTTP 404** (ไม่เปิดเผยว่ามีอยู่จริง)
- **Postconditions:** read-only
- **Business Rules:** ข้อมูลเป็น immutable — สะท้อนกฎ ณ เวลาที่คำนวณ; admin/service เข้าถึงได้ทุกรายการ

---

### UC-060 — บันทึก HTS code เป็นรายการโปรด

- **Use Case ID:** UC-060
- **Actor:** Registered User
- **Description:** บันทึก HTS code ไว้เข้าถึงเร็ว พร้อม note ได้
- **Preconditions:** ผู้ใช้ล็อกอินแล้ว (ต้องมี JWT — ไม่รองรับ API Key ล้วน)
- **Main Flow:**
  1. User ส่ง `POST /favorites` พร้อม hts_code และ note (ถ้ามี)
  2. ระบบตรวจว่ายังไม่เคยบันทึก
  3. ระบบบันทึกผูกกับ user_id และคืนผล (**HTTP 201**)
- **Exception Flow:**
  - 1a. ไม่ได้ล็อกอิน → **HTTP 401** `Login required to use favorites`
  - 2a. บันทึกซ้ำ → **HTTP 409** `HTS code already in favorites`
- **Postconditions:** HTS code อยู่ในรายการโปรดของผู้ใช้
- **Business Rules:** 1 ผู้ใช้ บันทึก 1 HTS code ได้ครั้งเดียว (ห้ามซ้ำ)

---

### UC-061 — ดู HTS code ที่บันทึกไว้

- **Use Case ID:** UC-061
- **Actor:** Registered User
- **Description:** แสดงรายการ HTS code โปรดของผู้ใช้ปัจจุบัน
- **Preconditions:** ผู้ใช้ล็อกอินแล้ว
- **Main Flow:**
  1. User ส่ง `GET /favorites`
  2. ระบบคืนรายการของผู้ใช้ เรียงตามเวลาบันทึกล่าสุดก่อน
- **Exception Flow:**
  - 1a. ไม่ได้ล็อกอิน → **HTTP 401**
- **Postconditions:** read-only
- **Business Rules:** แสดงเฉพาะรายการของผู้ใช้ที่ล็อกอินเท่านั้น

---

### UC-062 — ลบ HTS code ออกจากรายการโปรด

- **Use Case ID:** UC-062
- **Actor:** Registered User
- **Description:** ลบ HTS code ที่บันทึกไว้ออก
- **Preconditions:** ผู้ใช้ล็อกอินแล้ว; รายการนั้นเป็นของผู้ใช้
- **Main Flow:**
  1. User ส่ง `DELETE /favorites/{favorite_id}`
  2. ระบบตรวจว่ารายการเป็นของผู้ใช้และลบออก (**HTTP 204**)
- **Exception Flow:**
  - 1a. ไม่ได้ล็อกอิน → **HTTP 401**
  - 2a. ไม่พบรายการ / ไม่ใช่ของผู้ใช้ → **HTTP 404** `Favorite not found`
- **Postconditions:** รายการถูกลบออกจากรายการโปรด
- **Business Rules:** ลบได้เฉพาะรายการของตนเอง

---

### UC-070 — เปรียบเทียบผลการคำนวณหลายกรณี (Frontend)

- **Use Case ID:** UC-070
- **Actor:** Registered User
- **Description:** เปรียบเทียบต้นทุนนำเข้าระหว่างหลายกรณี (เช่น วันที่นำเข้าต่างกัน หรือสินค้าต่างกัน) ที่หน้า Compare
- **Preconditions:** ผู้ใช้ล็อกอินแล้ว; มีผลการคำนวณตั้งแต่ 2 กรณีขึ้นไป
- **Main Flow:**
  1. User เข้าหน้า `/compare`
  2. User เลือก/ป้อนกรณีที่จะเทียบ
  3. Frontend เรียก `POST /calculate` ต่อกรณี แล้วแสดงผลเทียบกันเป็นตาราง
- **Alternative Flow:**
  - 3a. ผู้ใช้เพิ่ม/ลบกรณีระหว่างทาง → ตารางอัปเดต
- **Exception Flow:**
  - 3b. กรณีใดคำนวณล้มเหลว (เช่น HTS ไม่พบ) → แสดง error เฉพาะกรณีนั้น
  - 3c. **[ใหม่]** ถ้าการเทียบหลายกรณีทำให้ใช้โควตาต่อวันเกิน → กรณีที่เกินได้ **HTTP 429**
- **Postconditions:** ผู้ใช้เห็นผลเปรียบเทียบ (แต่ละการคำนวณถูกบันทึก audit และนับโควตา)
- **Business Rules:** อ้างอิงกฎธุรกิจของ UC-010 ทุกข้อ (รวม BR-7 โควตา)
- **หมายเหตุ:** เป็น flow ฝั่ง frontend ที่ประกอบ (include) UC-010 หลายครั้ง

---

### UC-071 — พิมพ์ / ส่งออกผลลัพธ์เป็น PDF (Frontend)

- **Use Case ID:** UC-071
- **Actor:** Registered User
- **Description:** ส่งออก/พิมพ์รายงานผลการคำนวณเป็น PDF (หน้า `/print`, ใช้ `export-pdf.ts`)
- **Preconditions:** มีผลการคำนวณที่ต้องการพิมพ์
- **Main Flow:**
  1. User กด Export/Print จากผลการคำนวณ
  2. Frontend จัดรูปแบบรายงานและสร้าง PDF
  3. ผู้ใช้บันทึก/พิมพ์ไฟล์
- **Exception Flow:** —
- **Postconditions:** ผู้ใช้ได้ไฟล์ PDF ของรายงาน
- **Business Rules:** —

---

### UC-080 — ดูรายชื่อผู้ใช้ทั้งหมด *(admin)* — ใหม่

- **Use Case ID:** UC-080
- **Actor:** Admin / API Client (trusted service)
- **Description:** แสดงรายชื่อผู้ใช้ทั้งหมดในระบบ เรียงตามวันที่สร้างล่าสุดก่อน
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin
- **Main Flow:**
  1. Client ส่ง `GET /users?limit=...&offset=...`
  2. ระบบตรวจสิทธิ์ admin และคืนรายการผู้ใช้ (id, email, name, role, daily_calculations, ฯลฯ)
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403** `Admin role required`
- **Postconditions:** read-only
- **Business Rules:** limit ≤ 200, มี pagination

---

### UC-081 — ดูข้อมูลผู้ใช้รายคน *(admin)* — ใหม่

- **Use Case ID:** UC-081
- **Actor:** Admin / API Client (trusted service)
- **Description:** ดึงข้อมูลผู้ใช้รายคนตาม id
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin
- **Main Flow:**
  1. Client ส่ง `GET /users/{user_id}`
  2. ระบบตรวจสิทธิ์ admin และคืนข้อมูลผู้ใช้
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. ไม่พบ user_id → **HTTP 404** `User '...' not found`
- **Postconditions:** read-only
- **Business Rules:** —

---

### UC-082 — เปลี่ยน role ผู้ใช้ (promote/demote admin) *(admin)* — ใหม่

- **Use Case ID:** UC-082
- **Actor:** Admin
- **Description:** เลื่อนหรือลดสิทธิ์ผู้ใช้ระหว่าง `user` และ `admin`
- **Preconditions:** ผ่านการยืนยันตัวตนแบบ admin; ผู้ใช้เป้าหมายมีอยู่
- **Main Flow:**
  1. Admin ส่ง `PUT /users/{user_id}/role` พร้อม role ใหม่ (`user` หรือ `admin`)
  2. ระบบตรวจสิทธิ์ admin และ validate role
  3. ระบบตรวจว่าไม่ใช่การลด role ของบัญชีตัวเอง
  4. ระบบอัปเดต role และคืนข้อมูลผู้ใช้
- **Alternative Flow:**
  - Promote: `user` → `admin` (ผู้ใช้ได้สิทธิ์จัดการข้อมูลอ้างอิงและเห็นประวัติทุกคน)
  - Demote: `admin` → `user` (ยกเลิกสิทธิ์ admin ของผู้ใช้อื่น)
- **Exception Flow:**
  - 2a. ผู้ใช้ทั่วไป → **HTTP 403**
  - 2b. role ไม่ถูกต้อง (ไม่ใช่ user/admin) → **HTTP 400** `Invalid role '...'`
  - 2c. ไม่พบ user_id → **HTTP 404**
  - **3a. admin พยายามลด role ของตัวเอง** → **HTTP 400** `You cannot remove your own admin role.`
- **Postconditions:** role ของผู้ใช้เป้าหมายถูกเปลี่ยน มีผลกับ token ที่ออกใหม่ (access token เดิมยังฝัง role เก่าจนหมดอายุ/refresh)
- **Business Rules:**
  - role ที่รองรับมีเพียง `user` และ `admin`
  - admin ลด role ของตัวเองไม่ได้ (กันระบบล็อกตัวเองออกจาก admin คนสุดท้าย)
  - เนื่องจาก JWT เก็บ role ไว้ในตัว token (อายุ 15 นาที) การเปลี่ยน role จะมีผลเต็มที่หลังผู้ใช้ refresh token (UC-002)

---

## D. Use Case Diagram (อธิบายเป็นข้อความ)

### ความสัมพันธ์ Actor → Use Case

```
Guest
  └── UC-001 เข้าสู่ระบบด้วย OAuth ──<<include>>──► (ยืนยันตัวตนกับ Google/GitHub)

Registered User (role = user)
  ├── UC-002 ต่ออายุ Token   ├── UC-003 ดูโปรไฟล์   ├── UC-004 ออกจากระบบ
  ├── UC-010 คำนวณ Landed Cost ⭐ (ภายในโควตาต่อวัน)
  ├── UC-020 ค้นหา HTS   ├── UC-021 ดูรายละเอียด HTS
  ├── UC-030 ดูกฎภาษี    ├── UC-034 ดู Exclusions   ├── UC-040 ดู FX
  ├── UC-050 ดูประวัติ (เฉพาะของตน)   ├── UC-051 ดูรายละเอียดการคำนวณ (เฉพาะของตน)
  ├── UC-060/061/062 จัดการ Favorites
  ├── UC-070 เปรียบเทียบ   └── UC-071 พิมพ์/ส่งออก PDF

Admin (role = admin — สืบทอดทุกอย่างของ User + จัดการข้อมูลอ้างอิง + จัดการผู้ใช้ + เห็นประวัติทุกคน)
  ├── UC-022 เพิ่ม HTS   ├── UC-023 แก้ไข HTS   ├── UC-024 ลบ HTS (มี referential guard)
  ├── UC-031 สร้างกฎภาษี  ├── UC-032 แก้ไขกฎภาษี  ├── UC-033 ลบกฎภาษี  ├── UC-038 ปิดกฎภาษี
  ├── UC-035 สร้าง Exclusion  ├── UC-036 แก้ไข Exclusion  ├── UC-037 ลบ Exclusion  ├── UC-039 ปิด Exclusion
  ├── UC-041 เพิ่ม/อัปเดต FX   ├── UC-042 ลบ FX
  ├── UC-080 ดูรายชื่อผู้ใช้   ├── UC-081 ดูผู้ใช้รายคน   ├── UC-082 เปลี่ยน role ผู้ใช้
  └── UC-050/051 ดูประวัติการคำนวณของทุกคน

API Client / Service (ผ่าน X-API-Key ที่ถูกต้อง = trusted service)
  └── เรียกได้ทั้ง read และ write endpoint (ผ่านด่าน require_admin), เห็นประวัติทั้งหมด, ไม่ผูกโควตา

OAuth Provider (Google/GitHub) ── Actor รอง ── เกี่ยวข้องกับ UC-001
FX Rate Source ── Actor รอง ── เกี่ยวข้องกับ UC-010 (แปลงสกุลเงิน)
```

### ความสัมพันธ์ `<<include>>` และ `<<extend>>`

- **UC-010 คำนวณ Landed Cost** `<<include>>`:
  - "ตรวจโควตาต่อวัน" (สำหรับผู้ใช้ล็อกอิน)
  - "ตรวจสอบรหัส HTS"
  - "แปลงสกุลเงิน CNY→USD" (ผ่าน FX Rate Source)
  - "ดึงกฎภาษีที่มีผล + ใช้ Stacking Logic" (Rule Engine)
  - "ตรวจ Exclusion"
  - "บันทึก Audit Log พร้อม user_id" (สร้างข้อมูลให้ UC-050/051)
- **UC-010** `<<extend>>` (เงื่อนไขพิเศษ):
  - "ยกเว้นแบบ De minimis" (extend เมื่อมูลค่า ≤ $800)
  - "ยกเว้น MFN ภายใต้ USMCA" (extend เมื่อ origin = MX/CA)
- **UC-070 เปรียบเทียบ** `<<include>>` **UC-010** (เรียกซ้ำหลายกรณี)
- **UC-071 พิมพ์/ส่งออก** `<<extend>>` ผลลัพธ์ของ **UC-010**
- **UC-001 OAuth Login** `<<include>>` "ออก JWT" ซึ่งเป็น precondition ของทุก UC ที่ต้องล็อกอิน
- ทุก UC แบบ **admin** (UC-022/023/024/031/032/033/035/036/037/038/039/041/042 และ UC-080/081/082) `<<include>>` "ตรวจสิทธิ์ Admin (require_admin)"
- ทุก UC แบบ **read** `<<include>>` "ตรวจสิทธิ์ (require_api_key / JWT)"
- **UC-024 ลบ HTS** `<<include>>` "ตรวจ referential guard (นับกฎภาษี/exclusion ที่อ้างถึง)"
- **UC-033 ลบกฎภาษี / UC-037 ลบ Exclusion** `<<extend>>` "กัน hard delete ของที่มีผลแล้ว (แนะ soft-close UC-038/039)"
- **UC-082 เปลี่ยน role** `<<extend>>` "กันการลด role ตัวเอง"

---

## E. ตาราง Summary ของ Use Case ทั้งหมด

| ID | ชื่อ Use Case | Actor หลัก | Endpoint / หน้าจอ | สิทธิ์ | Priority |
|----|----------------|------------|-------------------|--------|----------|
| UC-001 | เข้าสู่ระบบด้วย OAuth | Guest | `/auth/login/*`, `/auth/callback/*` | สาธารณะ | High |
| UC-002 | ต่ออายุ Access Token | User | `POST /auth/refresh` | มี refresh token | Medium |
| UC-003 | ดูโปรไฟล์ผู้ใช้ | User | `GET /auth/me` | ล็อกอิน | Medium |
| UC-004 | ออกจากระบบ | User | `POST /auth/logout` | ล็อกอิน | Low |
| UC-010 | คำนวณ Landed Cost ⭐ | User / API | `POST /calculate` | auth + โควตา | **Critical** |
| UC-020 | ค้นหา HTS | User / API | `GET /hts-codes` | auth | High |
| UC-021 | ดูรายละเอียด HTS | User / API | `GET /hts-codes/{code}` | auth | Medium |
| UC-022 | เพิ่ม HTS | Admin | `POST /hts-codes` | admin | Medium |
| UC-023 | แก้ไข HTS | Admin | `PUT /hts-codes/{code}` | admin | Low |
| UC-024 | ลบ HTS | Admin | `DELETE /hts-codes/{code}` | admin | Low |
| UC-030 | ดูกฎภาษี | User / Admin | `GET /tariff-rules` | auth | High |
| UC-031 | สร้างกฎภาษี | Admin | `POST /tariff-rules` | admin | High |
| UC-032 | แก้ไขกฎภาษี | Admin | `PUT /tariff-rules/{id}` | admin | High |
| UC-033 | ลบกฎภาษี | Admin | `DELETE /tariff-rules/{id}` | admin | Medium |
| UC-038 | ปิดกฎภาษี (soft-close) | Admin | `POST /tariff-rules/{id}/close` | admin | Medium |
| UC-034 | ดู Exclusions | User / Admin | `GET /exclusions` | auth | Medium |
| UC-035 | สร้าง Exclusion | Admin | `POST /exclusions` | admin | Medium |
| UC-036 | แก้ไข Exclusion | Admin | `PUT /exclusions/{id}` | admin | Low |
| UC-037 | ลบ Exclusion | Admin | `DELETE /exclusions/{id}` | admin | Low |
| UC-039 | ปิด Exclusion (soft-close) | Admin | `POST /exclusions/{id}/close` | admin | Low |
| UC-040 | ดู FX Rates | User / Admin | `GET /fx-rates` | auth | Medium |
| UC-041 | เพิ่ม/อัปเดต FX | Admin | `POST /fx-rates` | admin | High |
| UC-042 | ลบ FX | Admin | `DELETE /fx-rates/{id}` | admin | Low |
| UC-050 | ดูประวัติการคำนวณ | User / Admin | `GET /calculations` | auth (per-user) | Medium |
| UC-051 | ดูรายละเอียดการคำนวณ | User / Admin | `GET /calculations/{id}` | auth (ownership) | Medium |
| UC-060 | บันทึก Favorite | User | `POST /favorites` | ล็อกอิน (JWT) | Low |
| UC-061 | ดู Favorites | User | `GET /favorites` | ล็อกอิน (JWT) | Low |
| UC-062 | ลบ Favorite | User | `DELETE /favorites/{id}` | ล็อกอิน (JWT) | Low |
| UC-070 | เปรียบเทียบผลการคำนวณ | User | `/compare` (frontend) | ล็อกอิน | Medium |
| UC-071 | พิมพ์/ส่งออก PDF | User | `/print` (frontend) | ล็อกอิน | Low |
| UC-080 | ดูรายชื่อผู้ใช้ | Admin | `GET /users` | admin | Medium |
| UC-081 | ดูผู้ใช้รายคน | Admin | `GET /users/{id}` | admin | Low |
| UC-082 | เปลี่ยน role ผู้ใช้ | Admin | `PUT /users/{id}/role` | admin | High |

**รวม 32 Use Case** — ยืนยันจากโค้ดจริงทั้งหมด

---

## F. ข้อสังเกต / Roadmap / ต้องถาม Stakeholder

### ✅ ประเด็นที่แก้ไขแล้ว (v1.0 → v2.0)
1. **Admin gating บังคับใช้จริงแล้ว** — write endpoints (HTS, tariff rules, exclusions, FX) ใช้ `require_admin`; ผู้ใช้ทั่วไปได้ 403
2. **โควตาการคำนวณต่อวันทำงานแล้ว** — นับผ่าน `daily_calculations`/`last_calculation_date`, limit user=50 / admin=99,999 (ตั้งค่าได้), เกินได้ 429
3. **ประวัติการคำนวณแยกตามผู้ใช้แล้ว** — บันทึก `user_id` ลง log, ผู้ใช้ทั่วไปเห็นเฉพาะของตน, admin/service เห็นทั้งหมด, ตรวจ ownership ที่ระดับ detail
4. **CRUD ครบชุดขึ้น** — เพิ่ม Update/Delete ให้ HTS และ Exclusion, Delete ให้ Tariff Rule

### ✅ ประเด็นที่แก้ไขเพิ่มใน v3.0 (ปิดคำถามค้างจาก v2.0)
5. **จัดการสิทธิ์ผู้ใช้แล้ว (UC-080/081/082)** — admin ดูรายชื่อผู้ใช้และเปลี่ยน role (promote/demote) ได้ผ่าน API พร้อมกันการลด role ตัวเอง (ไม่ต้องแก้ DB ตรงๆ อีกต่อไป)
6. **FX Rate มี Delete แล้ว (UC-042)** — CRUD ครบทุก entity หลัก
7. **Referential guard สำหรับลบ HTS แล้ว (UC-024)** — ลบ HTS ที่ยังมีกฎภาษี/exclusion อ้างถึงไม่ได้ (คืน 409) กัน dangling reference

| Entity | Create | Read | Update | Delete |
|--------|:------:|:----:|:------:|:------:|
| HTS Code | ✅ | ✅ | ✅ | ✅ (มี referential guard) |
| Tariff Rule | ✅ | ✅ | ✅ | ✅ |
| Exclusion | ✅ | ✅ | ✅ | ✅ |
| FX Rate | ✅ (upsert) | ✅ | ✅ (upsert) | ✅ |
| User | — (auto จาก OAuth) | ✅ (admin) | ✅ (role เท่านั้น) | ❌ *(ดูคำถามข้อ 4)* |
| Favorite | ✅ | ✅ | ❌ | ✅ |
| Calculation | ✅ (auto) | ✅ | — (immutable ตั้งใจ) | — |

### ❓ ประเด็นที่ยังต้องยืนยันกับ Stakeholder
1. **โควตาสำหรับผู้เรียกแบบ API Key** — ปัจจุบัน API Key ไม่ผูกโควตาและเห็นประวัติทั้งหมด (ถือเป็น trusted service) — ตรงกับเจตนาธุรกิจหรือไม่?
2. **พฤติกรรม FX fallback** — กรณีไม่มีอัตราแลกเปลี่ยนในฐานข้อมูลเลย ระบบจะดึงจาก live API (frankfurter.app) ถ้ายังไม่ได้จะคืน 404 — ยืนยัน behavior นี้กับธุรกิจหรือไม่?
3. **ค่าโควตาต่อวัน** — user 50 / admin 99,999 เป็นค่าเริ่มต้น — ต้องการปรับตามแพ็กเกจ/ลูกค้าไหม?
4. **การลบผู้ใช้ (User delete)** — ยังไม่มี endpoint ลบผู้ใช้ (มีแค่เปลี่ยน role) — ต้องการหรือใช้ soft-disable แทน? และควรจัดการ favorites/calculation logs ของผู้ใช้นั้นอย่างไร?
5. **การลบกฎภาษี/exclusion กลางคัน (UC-033/037)** — ปัจจุบันลบได้ทันที (hard delete) ทางเลือกที่ปลอดภัยกว่าคือใช้ `effective_to` ปิดกฎ (soft-close) — ต้องการบังคับ soft-close ไหม?

### ✅ ประเด็นที่แก้ไขเพิ่มใน v3.1
8. **Soft-close สำหรับกฎภาษีและ exclusion แล้ว (UC-038/039)** — hard delete (UC-033/037) จำกัดเฉพาะรายการที่ยังไม่เคยมีผล; รายการที่มีผลแล้วต้องใช้ soft-close (ตั้ง `effective_to`) เพื่อรักษา audit trail — ตอบโจทย์ compliance โดยตรง

### ❓ ประเด็นที่ยังต้องยืนยันกับ Stakeholder (ปรับปรุง)
1. **โควตาสำหรับผู้เรียกแบบ API Key** — ปัจจุบัน API Key ไม่ผูกโควตาและเห็นประวัติทั้งหมด (ถือเป็น trusted service) — ตรงกับเจตนาธุรกิจหรือไม่?
2. **พฤติกรรม FX fallback** — กรณีไม่มีอัตราแลกเปลี่ยนในฐานข้อมูลเลย ระบบจะดึงจาก live API (frankfurter.app) ถ้ายังไม่ได้จะคืน 404 — ยืนยัน behavior นี้กับธุรกิจหรือไม่?
3. **ค่าโควตาต่อวัน** — user 50 / admin 99,999 เป็นค่าเริ่มต้น — ต้องการปรับตามแพ็กเกจ/ลูกค้าไหม?
4. **การลบผู้ใช้ (User delete)** — ยังไม่มี endpoint ลบผู้ใช้ (มีแค่เปลี่ยน role) — ต้องการหรือใช้ soft-disable แทน? และควรจัดการ favorites/calculation logs ของผู้ใช้นั้นอย่างไร?

### 🗺️ Roadmap (ยังไม่ implement — ไม่ได้ทำเป็น Use Case)
Batch calculation, Multi-origin support, Rule expiration alerts, Government data sync, Anti-dumping duties (AD/CVD มีใน type แล้วแต่ยังไม่มี flow เต็ม), Rate comparison mode

---

> **สรุป:** ระบบมี **32 Use Case** ที่ยืนยันจากโค้ดจริง โดย **UC-010 (คำนวณ Landed Cost)** เป็นหัวใจ
> ประเด็นค้างจาก v1.0 ทั้ง 4 ข้อ, คำถามนโยบายจาก v2.0 อีก 3 ข้อ (จัดการสิทธิ์ผู้ใช้, FX delete, referential guard)
> และเรื่อง soft-close เชิง compliance (v3.1) ได้รับการแก้ไขและยืนยันด้วยชุดทดสอบ (105 tests ผ่านทั้งหมด)
> ที่เหลือเป็นคำถามเชิงนโยบายกับ stakeholder และรายการ roadmap
