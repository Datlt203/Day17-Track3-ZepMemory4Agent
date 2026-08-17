# README_submission

Practice benchmark: student 11/11 PASS, hit rate 100.0%; no-memory 2/11 PASS. Comparison report: `reports/comparison.md`. Privacy drill ran after benchmark: delete and verify-only both showed `Zep user absent: True` and `Redis user keys remaining: 0`.

Layer quan trong nhat trong bo test nay la long-term memory. No truc tiep quyet dinh E02, E03, E08, E09 va con cung cap personal preference cho mixed case E07. E08 la case quan trong nhat ve conflict: constraint moi cho BLUEBIRD-42 bat buoc TypeScript/NestJS override generic Python preference trong scope company backend, nhung Python van con dung cho ORCHID-27.

Trade-off: Zep Context Block cho san user graph, thread context, fact/episode search, validity/provenance va user isolation nen phu hop cross-session recall. Redis + Qdrant de tu kiem soat va re hon cho baseline/local, nhung phai tu thiet ke schema, ranking, recency, conflict handling, deletion va privacy guardrail.

Guardrail chong memory poisoning: chi durable-write khi user opt-in, redact PII truoc ingest, gan source/timestamp/confidence cho moi memory, scope user/domain ro rang, va bat review cho preference/task co tac dong cao. Conflict khong xoa lich su; dung recency + scope + validity de chon fact hien hanh.

Phan tich benchmark: khong co layer yeu trong student run vi tat ca layers deu pass; baseline fail cac durable layer va chi pass short-term E01/E10. Case retrieve nhieu token nhat la E02 voi 1336 tokens. E07 can long-term + semantic: evidence bat buoc la `Python` va `Idempotency-Key`. Token reduction cua memory-enabled la 14.2%, thap hon no-memory 81.8% vi memory that su retrieve evidence; no-memory co reduction cao do lay gan nhu rong nhung hit rate chi 18.2%.

E10 compaction: sliding memory giu `REVIEW-DEADLINE-1600`, Friday va 16:00 trong durable notes sau 8 compactions. Buffer giu raw transcript nhung token tang tuyen tinh; compaction tot phai giu state, decision, TODO va constraint.
