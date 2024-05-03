def guess_emails(company_data: dict):
    emails = {}
    for company_website in company_data:
        suffix = company_website.replace("https://", "").replace("http://", "")
        suffix = suffix.split("/")[0]
        company_people = company_data[company_website]["company_people"]
        company_name = company_data[company_website]["company_name"]
        if suffix.startswith("www."):
            suffix = suffix[4:]
        for person in company_people:
            prefix = None
            person_name = str(person[0]).strip().lower()
            person_position = str(person[1]).strip().lower()
            for word in person_name.split(" "):
                if word.endswith("."):
                    continue
                if word == "linkedin":
                    break
                prefix = word
                break
            if prefix:
                email = f"{prefix}@{suffix}"
                emails[email] = [person_name, person_position, company_name]
    return emails
