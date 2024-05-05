def generate_possible_emails(person_name: str, company_domain: str):
    try:
        first_name, last_name = person_name.lower().split()
    except ValueError:
        if len(person_name.split()) == 1:
            first_name = person_name.lower()
            last_name = ""
        elif len(person_name.split()) > 2:
            first_name = person_name.lower().split()[0]
            last_name = person_name.lower().split()[1]
        else:
            first_name = ""
            last_name = ""
    first_initial = first_name[0]
    last_initial = last_name[0]
    email_variations = [
        # First name last name
        f"{first_name}.{last_name}@{company_domain}",
        f"{first_name}{last_name}@{company_domain}",
        f"{last_name}.{first_name}@{company_domain}",
        f"{last_name}{first_name}@{company_domain}",

       # First initial last name
        f"{first_initial}{last_name}@{company_domain}",
        f"{first_initial}.{last_name}@{company_domain}",
        f"{last_name}.{first_initial}@{company_domain}",
        f"{last_name}{first_initial}@{company_domain}",

        # First name last initial
        f"{first_name}{last_initial}@{company_domain}",
        f"{first_name}.{last_initial}@{company_domain}",
        f"{last_initial}{first_name}@{company_domain}",
        f"{last_initial}.{first_name}@{company_domain}",

        # First initial last initial
        f"{first_initial}.{last_initial}@{company_domain}",
        f"{first_initial}{last_initial}@{company_domain}",
        f"{last_initial}{first_initial}@{company_domain}",
        f"{last_initial}.{first_initial}@{company_domain}",

        # only one value
        f"{first_initial}@{company_domain}",
        f"{last_initial}@{company_domain}",
        f"{first_name}@{company_domain}",
        f"{last_name}@{company_domain}",
    ]
    return email_variations
