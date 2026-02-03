# Backend Bookshop - Django

A production-oriented backend for an online bookstore, built with Django and designed to demonstrate real-world e-commerce architecture, clean code practices, and scalability considerations.

This project is intended as a professional portfolio piece for international freelance and backend roles.

---

## Overview

Backend Bookshop is a Django-based e-commerce system that handles:

- User authentication (email / phone-based)
- Product catalog management
- Shopping cart and order lifecycle
- Secure payment processing with Stripe
- Admin management via a customized Django admin panel

The focus of this project is backend correctness, clarity, and extensibility, not frontend visuals.

---

## Key Features

### Authentication
- User registration and login via email or phone number
- Custom user model
- Permission-aware admin access

### Product & Catalog
- Books, authors, categories, and tags
- Search and filtering support
- Extendable data model for future API usage

### Shopping Cart & Orders
- Persistent cart logic
- Quantity management
- Order creation tied to authenticated users
- Clear separation between cart and order state

### Payments
- Stripe integration for secure checkout
- Payment intent–based flow
- Order status updates after successful payment

### Admin Panel
- Customized Django admin UI
- Fine-grained access control
- Optimized workflows for managing products and orders

---

## Tech Stack

- Backend: Django
- Database: SQLite (development), PostgreSQL (production-ready)
- Payments: Stripe
- Deployment-ready: PythonAnywhere, Render, Railway, Heroku
- Version Control: Git & GitHub

---

## Project Structure

The project follows a modular Django structure with a clear separation of concerns between:

- authentication
- store / catalog logic
- orders & payments
- admin customization

This structure makes the codebase suitable for API expansion, scaling, and team collaboration.

---

## Running Locally

```bash
git clone https://github.com/AMIN-AKR0/Backend-Bookshop-django.git
cd Backend-Bookshop-django
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```


- Access the site at: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Deployment Notes

This project can be deployed on platforms such as PythonAnywhere, Render, Railway, or Heroku.

For production deployments:
- Use PostgreSQL instead of SQLite
- Set DEBUG = False
- Configure secure ALLOWED_HOSTS
- Enable HTTPS (handled by most hosting providers)
- Use Stripe webhooks for reliable payment confirmation

---

## Future Improvements

Planned enhancements include:

- Full REST API using Django REST Framework
- AI-based book recommendations  
  (content-based filtering using tags, purchase history, and cosine similarity)
- Stripe webhook integration for robust payment events
- Comprehensive unit and integration testing
- Guest checkout support
- Additional payment gateways
- Improved security (rate limiting, CAPTCHA, hardened authentication flows)

---

## Contributing

Pull requests are welcome.  
For major changes, please open an issue to discuss the proposal first.

---

## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## Contact

- GitHub: [@AMIN-AKR0](https://github.com/AMIN-AKR0)
- Telegram: [@AMIN_AKR0](https://t.me/AMIN_AKR0/)
- Email: [aminak.dev@gmail.com](mailto:aminak.dev@gmail.com)

For freelance inquiries, open a GitHub issue or contact directly.

---

Last updated: February 2026