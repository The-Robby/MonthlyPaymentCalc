import PySimpleGUI as sg
import json
import os
import sys

sg.theme('DarkAmber')   # Add a touch of color

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = 'Spendings.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = []

    return data

def save_data(data):
    with open(DATA_FILE, 'w') as json_file:
        json.dump(data, json_file, indent=2)

# Windows functions
def add_attribute():
    layout_add_attribute = [
        [sg.Text('What do you want to call this attribute?'), sg.InputText(key='-NAME-')],
        [sg.Text('How much do you spend on...?'), sg.InputText(key='-VALUE-')],
        [sg.Text('Execution Date (optional):'), sg.InputText(key='-DATE-')],
        [sg.Text('Type:'), sg.DropDown(values=['Monthly', 'Quarterly', 'Yearly'], key='-TYPE-', default_value='Monthly')],
        [sg.Button('Ok'), sg.Button('Cancel')]
    ]

    windowAttribute = sg.Window('Monthly Payments', layout_add_attribute)

    while True:
        event, values = windowAttribute.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':  # if the user closes the window or clicks cancel
            break

        if event == 'Ok':
            attribute_name = values['-NAME-']
            attribute_value_str = values['-VALUE-']
            attribute_date = values['-DATE-']
            attribute_type = values['-TYPE-']

            try:
                attribute_value = float(attribute_value_str)
            except ValueError:
                sg.popup_error('Please enter a valid numeric value for the attribute.')
                continue

            data = load_data()

            # Add new attribute to the data
            new_attribute = {
                "name": attribute_name,
                "value": attribute_value,
                "date": attribute_date,
                "type": attribute_type
            }

            data.append(new_attribute)

            save_data(data)
            break

    windowAttribute.close()
 
def remove_attribute():
    data = load_data()

    # Create a list of attribute names for the Listbox
    attribute_names = [attribute['name'] for attribute in data]

    layout_remove_attribute = [
        [sg.Text('Select an attribute to remove:')],
        [sg.Listbox(values=attribute_names, size=(40, 15), key='-ATTRIBUTE_LIST-', enable_events=True)],
        [sg.Button('Remove'), sg.Button('Cancel')]
    ]

    windowRemove = sg.Window('Monthly Payments - Remove Attribute', layout_remove_attribute, finalize=True)

    while True:
        event, values = windowRemove.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break

        if event == 'Remove':
            selected_indices = values['-ATTRIBUTE_LIST-']

            if not selected_indices:
                sg.popup_error("Please select an attribute to remove.")
                continue

            selected_index = selected_indices[0]

            if sg.popup_yes_no(f"Are you sure you want to remove the attribute '{selected_index}'?", title='Confirm Removal') == 'Yes':
                # Find the index of the selected attribute name in the list
                index_to_remove = attribute_names.index(selected_index)

                # Remove the selected attribute
                data.pop(index_to_remove)

                # Save the updated data to the JSON file
                save_data(data)

                sg.popup_ok(f"Attribute '{selected_index}' has been removed.")
                break

    windowRemove.close()

def update_attribute():
    data = load_data()

    # Create a list of attribute names for the Listbox
    attribute_names = [attribute['name'] for attribute in data]

    layout_update_attribute = [
        [sg.Text('Select an attribute to update:')],
        [sg.Listbox(values=attribute_names, size=(40, 15), key='-ATTRIBUTE_LIST-', enable_events=True)],
        [sg.Button('Update'), sg.Button('Cancel')]
    ]

    windowUpdateAttribute = sg.Window('Monthly Payments - Update Attribute', layout_update_attribute, finalize=True)

    while True:
        event, values = windowUpdateAttribute.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break

        if event == 'Update':
            selected_indices = values['-ATTRIBUTE_LIST-']

            if not selected_indices:
                sg.popup_error("Please select an attribute to update.")
                continue

            selected_index = selected_indices[0]
            original_attribute_name = selected_index
            original_attribute = next(attr for attr in data if attr['name'] == original_attribute_name)

            layout_update_details = [
                [sg.Text(f'Updating attribute: {original_attribute_name}')],
                [sg.Text('New name:'), sg.InputText(default_text=original_attribute['name'], key='-NEW_NAME-')],
                [sg.Text('New value:'), sg.InputText(default_text=str(original_attribute['value']), key='-NEW_VALUE-')],
                [sg.Text('New execution date (optional):'), sg.InputText(default_text=original_attribute.get('date', ''), key='-NEW_DATE-')],
                [sg.Text('New type (optional):'), sg.DropDown(values=['Monthly', 'Bi-Monthly', 'Quarterly', 'Yearly'], default_value=original_attribute.get('type', ''), key='-NEW_TYPE-')],
                [sg.Button('Apply Update')]
            ]

            windowUpdateDetails = sg.Window('Monthly Payments - Update Details', layout_update_details)

            while True:
                event_details, values_details = windowUpdateDetails.read()

                if event_details == sg.WIN_CLOSED:
                    break

                if event_details == 'Apply Update':
                    try:
                        new_value = float(values_details['-NEW_VALUE-'])
                    except ValueError:
                        sg.popup_error('Please enter a valid numeric value for the attribute.')
                        continue

                    updated_attribute = {
                        "name": values_details['-NEW_NAME-'],
                        "value": new_value,
                        "date": values_details['-NEW_DATE-'],
                        "type": values_details['-NEW_TYPE-']
                    }

                    data[data.index(original_attribute)] = updated_attribute
                    save_data(data)

                    sg.popup_ok(f"Attribute '{original_attribute_name}' has been updated.")
                    break

            windowUpdateDetails.close()

    windowUpdateAttribute.close()

def check_spendings():
    data = load_data()

    # Display details for every attribute
    attributes_list = []
    for attribute in data:
        attribute_details = f"{attribute['name']}: {attribute['value']} | Date: {attribute.get('date', 'N/A')} | Type: {attribute.get('type', 'N/A')}"
        attributes_list.append(attribute_details)

    # Calculate and display totals
    monthly_total = round(sum(attribute['value'] for attribute in data if attribute.get('type') == 'Monthly'), 2)
    quarterly_total = round(sum(attribute['value'] for attribute in data if attribute.get('type') in ('Quarterly')) + 3  * monthly_total, 2)
    quarterly_only_total = round(sum(attribute['value'] for attribute in data if attribute.get('type') in ('Quarterly')), 2)
    yearly_total = round(
        sum(attribute['value'] for attribute in data if attribute.get('type') == 'Yearly') +
        12 * monthly_total +
        4 * quarterly_only_total, 2)
    yearly_only_total = round(sum(attribute['value'] for attribute in data if attribute.get('type') == 'Yearly'), 2)
    monthly_ifall_total = round(sum(attribute['value'] for attribute in data if attribute.get('type') == 'Monthly') + quarterly_only_total / 3 + yearly_only_total / 12, 2)

    totals_list = [
        "Totals:",
        f"Monthly Total: {monthly_total}",
        f"Monthly If All Would Be Monthly Total: {monthly_ifall_total}",
        f"Quarterly Total: {quarterly_total}",
        f"Quarterly Only Total: {quarterly_only_total}",
        f"Yearly Total: {yearly_total}",
        f"Yearly Only Total: {yearly_only_total}"
    ]

    # Create the layout with Listbox
    layout_check_spendings = [
        [sg.Listbox(values=attributes_list, size=(80, 14))],
        [sg.Listbox(values=totals_list, size=(80, 7))],
        [sg.Button('Cancel')]
    ]

    windowCheckSpendings = sg.Window('Monthly Payments - Check Spendings', layout_check_spendings, finalize=True)

    event, values = windowCheckSpendings.read()

    windowCheckSpendings.close()

def main():
    layout_main = [
        [sg.Text('Do you want to add an attribute or remove one?')],
        [sg.Button('Add'), sg.Button('Update'), sg.Button('Remove'), sg.Button('Check spendings')],
        [sg.Text('Exit:'), sg.Button('Cancel')]
    ]

    windowMain = sg.Window('Monthly Payments', layout_main)

    while True:
        event, values = windowMain.read()

        if event == 'Add':
            add_attribute()
        
        if event == 'Update':
            update_attribute()

        if event == 'Remove':
            remove_attribute()

        if event == 'Check spendings':
            check_spendings()

        if event == sg.WIN_CLOSED or event == 'Cancel':  # if the user closes the window or clicks cancel
            break

    windowMain.close()


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Load existing data when the script starts
data = load_data()

# Run the main function
main()
