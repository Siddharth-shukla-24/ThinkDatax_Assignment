# Sample Outreach Emails [DEMO / NOT SENT]

These examples demonstrate the fixed Appendix A outreach structure using publicly available corporate leadership announcements and company research. Each sample was generated directly from the platform's `render_email()` implementation (`app.services.email_template.py`) using grounded tokens extracted from public research.

**Important:** These samples are for demonstration only (`DEMO / NOT SENT`). They were never transmitted to the referenced individuals. No personal email addresses, phone numbers, or private contact details are collected, stored, or contacted.

---

## 1. Target - Cara Sylvester [DEMO / NOT SENT]

**Research source:** Target corporate leadership announcement and leadership directory (`https://corporate.target.com/about/leadership-team/cara-sylvester`).

**Observed signal:** Target named Cara Sylvester chief merchandising officer effective February 2026.

**Grounded context:** Her remit spans assortment, product development, product design, partner collaborations, and merchandising capabilities.

**Subject:** Target's new Chief Merchandising Officer - quick question

Hi Cara,

I noticed Target named Cara Sylvester chief merchandising officer effective February 2026.

At StyleSense AI, we help apparel and fashion brands and retailers teams support assortment design.

Given Target's assortment and product development, your merchandising team may be balancing assortment and product development.

Would you be open to a 15-minute call to see if it's a fit?

Best,
Alex Rivera
StyleSense AI

**Research basis:** Target's official leadership announcement confirms Cara Sylvester's role as Chief Merchandising Officer overseeing assortment, product design, and merchandising capabilities.

---

## 2. Under Armour - Kara Trent [DEMO / NOT SENT]

**Research source:** Under Armour corporate governance and executive leadership announcement (`https://about.underarmour.com/en/investors/corporate-governance.html`).

**Observed signal:** Under Armour says Kara Trent has served as chief merchandising officer since February 2026.

**Grounded context:** Her background includes North America merchandising and EMEA merchandising and planning roles driving product, brand and marketplace engines.

**Subject:** Under Armour's new Chief Merchandising Officer - quick question

Hi Kara,

I noticed Under Armour says Kara Trent has served as chief merchandising officer since February 2026.

At StyleSense AI, we help apparel and fashion brands and retailers teams support merchandising and planning.

Given Under Armour's product, brand and marketplace engines, your team may be coordinating product and merchandising planning across markets.

Would you be open to a 15-minute call to see if it's a fit?

Best,
Alex Rivera
StyleSense AI

**Research basis:** Under Armour's investor relations and corporate governance disclosures verify Kara Trent's appointment as Chief Merchandising Officer across product, brand, and marketplace engines.

---

## 3. lululemon - Elizabeth Binder [DEMO / NOT SENT]

**Research source:** lululemon corporate leadership directory (`https://corporate.lululemon.com/about-us/leadership-team`).

**Observed signal:** lululemon identifies Elizabeth Binder as chief merchandising officer.

**Grounded context:** She leads global product strategy and assortment architecture and oversees global and regional merchandising teams and planning operations.

**Subject:** lululemon's Chief Merchandising Officer - quick question

Hi Elizabeth,

I noticed lululemon identifies Elizabeth Binder as chief merchandising officer.

At StyleSense AI, we help apparel and fashion brands and retailers teams support assortment architecture and planning.

Given lululemon's global and regional merchandising teams, your team may be coordinating assortment planning across regions.

Would you be open to a 15-minute call to see if it's a fit?

Best,
Alex Rivera
StyleSense AI

**Research basis:** lululemon's corporate leadership page documents Elizabeth Binder as Chief Merchandising Officer overseeing global and regional merchandising teams and assortment planning.

---

## Notes & Compliance

- **Exact Code Parity:** Every email above is generated verbatim from `render_email(lead, company)` in `backend/app/services/email_template.py`.
- **Locked Skeleton:** Preserves the Appendix A greeting, four-sentence order, product name (`StyleSense AI`), and sign-off.
- **Enforced Grounding:** Every bracketed token resolves strictly to verified corporate research stored on the company/lead models; unverified claims are dropped by the grounding check rather than hallucinated.
- **Data Privacy & Section 8 Compliance:** All research inputs are strictly public executive announcements. No private personal data or real personal email addresses are used, stored, or sent to.
