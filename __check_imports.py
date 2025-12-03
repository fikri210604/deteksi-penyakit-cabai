try:
    import controllers.admin_controller as ac
    print("OK admin_controller")
except Exception as e:
    print("ERR admin_controller:", e)

try:
    import controllers.admin.rule_controller as rc
    print("OK rule_controller")
except Exception as e:
    print("ERR rule_controller:", e)

