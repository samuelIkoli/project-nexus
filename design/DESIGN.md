## This is the schema as well as the dbml language used to design the visual representation on [dbdiagram.io](https://dbdiagram.io/)

```
Table users {
  id uuid [primary key]
  email varchar [not null, unique]
  password_hash varchar [not null]
  role varchar [not null, note: 'TEACHER | LEARNER | ADMIN']
  full_name varchar
  is_active boolean [not null, default: true]
  created_at timestamp [not null]
}

Table courses {
  id uuid [primary key]
  teacher_id uuid [not null, note: 'FK -> users.id (role should be TEACHER)']
  title varchar [not null]
  description text
  price_amount decimal [not null, default: 0.00]
  currency varchar [not null, default: 'USD', note: 'ISO 4217 e.g. USD, NGN']
  is_published boolean [not null, default: false]
  thumbnail_url varchar
  created_at timestamp [not null]
  updated_at timestamp [not null]
}

Table lessons {
  id uuid [primary key]
  course_id uuid [not null]
  title varchar [not null]
  video_url varchar [not null]
  position int [not null, note: 'Order of lesson within a course (1..n)']
  duration_seconds int
  is_free_preview boolean [not null, default: false]
  created_at timestamp [not null]
}

Table enrollments {
  id uuid [primary key]
  learner_id uuid [not null, note: 'FK -> users.id (role should be LEARNER)']
  course_id uuid [not null]
  status varchar [not null, default: 'ACTIVE', note: 'ACTIVE | REVOKED | REFUNDED']
  created_at timestamp [not null]
}

Table payments {
  id uuid [primary key]
  learner_id uuid [not null]
  course_id uuid [not null]
  amount decimal [not null]
  currency varchar [not null, default: 'USD']
  provider varchar [not null, note: 'PAYSTACK | STRIPE | CHAPA | FLUTTERWAVE | MANUAL']
  provider_reference varchar [unique, note: 'External transaction reference/id']
  status varchar [not null, default: 'PENDING', note: 'PENDING | SUCCESS | FAILED | CANCELLED | REFUNDED']
  created_at timestamp [not null]
}

Table course_reviews {
  id uuid [primary key]
  learner_id uuid [not null]
  course_id uuid [not null]
  rating int [not null, note: '1..5']
  comment text
  created_at timestamp [not null]
}

Table teacher_reviews {
  id uuid [primary key]
  learner_id uuid [not null]
  teacher_id uuid [not null, note: 'FK -> users.id (role should be TEACHER)']
  rating int [not null, note: '1..5']
  comment text
  created_at timestamp [not null]
}

Ref: courses.teacher_id > users.id // many-to-one (teacher -> courses)
Ref: lessons.course_id > courses.id // many-to-one (course -> lessons)
Ref: enrollments.learner_id > users.id // many-to-one (learner -> enrollments)
Ref: enrollments.course_id > courses.id // many-to-one (course -> enrollments)
Ref: payments.learner_id > users.id // many-to-one (learner -> payments)
Ref: payments.course_id > courses.id // many-to-one (course -> payments)
Ref: course_reviews.learner_id > users.id // many-to-one (learner -> course reviews)
Ref: course_reviews.course_id > courses.id // many-to-one (course -> course reviews)
Ref: teacher_reviews.learner_id > users.id // many-to-one (learner -> teacher reviews)
Ref: teacher_reviews.teacher_id > users.id // many-to-one (teacher -> teacher reviews)
```