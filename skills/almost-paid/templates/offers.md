# Offer drafts per segment

Placeholders in `{braces}`. Keep every price, code and expiry pointing at one
source in the billing system — if the discount is edited later and the email
isn't, the email lies. Every email carries a working unsubscribe; every link
carries an expiry the link enforces.

Voice: short, plain, one CTA. Say what stopped them, not how great the
product is — they already know.

---

## 1 · Checkout abandoned — resume link, no discount

**Push (same day)**
> You were one tap away. Your {plan} is still here → {resume_link}

**Email (day 2)**
Subject: `your {plan} is waiting`

> Hi {first_name},
>
> You opened checkout for {plan} on {day}. Nothing was charged.
>
> If you got interrupted, this takes you straight back: {resume_link}
>
> If something on the checkout page put you off, reply to this email and tell me what — I read every one.
>
> {sender_name}

---

## 2 · Payment failed — retry, never discount

**Email (immediately)**
Subject: `your payment didn't go through`

> Hi {first_name},
>
> Your {plan} payment on {day} was declined by the card issuer ({reason_if_known}). Your access is {still active until {date} / paused}.
>
> Update your card here: {retry_link}
>
> Nothing else changes; the plan and price stay as they were.

**Push (day 1)**
> Your {plan} payment didn't go through — update your card to keep access → {retry_link}

---

## 3 · Hit the wall mid-task — finish-the-task credit

**Push (same day)**
> You were mid-{task} when you ran out of {credits}. We added {n} so you can finish → {deep_link_to_task}

*(No pitch. The upgrade prompt appears naturally when they finish.)*

---

## 4 · Paywall, repeated — value-add, time-boxed

**Email**
Subject: `{feature} is open for you until {date}`

> Hi {first_name},
>
> You've looked at {feature} a few times. Instead of asking you to decide now, we opened it: it's yours until {date}, no card needed.
>
> {open_link}
>
> After that it goes back behind {plan} at {price}/{period}.

**Reminder (day 3)**
> {feature} closes for you {tomorrow / on {date}} → {open_link}

---

## 5 · Trial lapsed — time-boxed discount, once

**Email (day 1)**
Subject: `come back at {discount}% off — until {expiry_date}`

> Hi {first_name},
>
> Your trial ended on {day}. During it you {what_they_did — e.g. "built 14 outfits"}.
>
> If price was the reason: {plan} at {discounted_price} for the first {period}, then {full_price}/{period}. Applies automatically at this link, until {expiry_date}:
>
> {discount_link}
>
> If it wasn't price, I'd genuinely like to know what it was — just reply.

**Email (day 5)**
Subject: `expires tomorrow`

> The {discount}% off {plan} ends {tomorrow}. {discount_link}

---

## 6 · Paywall once — no paid offer

**Email**
Subject: `{a genuinely useful thing, e.g. "how to get the most out of {feature}"}`

> {one useful tip or piece of content, no discount; the CTA is to use the product, not to buy}

---

## Compliance checklist (every send)

- [ ] price / code / expiry match what billing will actually charge
- [ ] link enforces the expiry
- [ ] unsubscribe works and is honoured within the legal window
- [ ] sender address is monitored (replies are a feature)
- [ ] hold-out logged
- [ ] no one contacted twice inside 14 days across campaigns
