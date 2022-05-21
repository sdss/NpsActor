import asyncio

import pytest

from lvmnps.actor.actor import lvmnps as NpsActor


@pytest.mark.asyncio
async def test_onoff(switches, actor: NpsActor):

    assert switches[0].name == "nps_dummy_1"
    assert switches[0].outlets[0].name == "port1"
    assert switches[0].outlets[0].state == -1
    switches[0].outlets[0].state = 0
    assert switches[0].outlets[0].state == 0

    # switch on nps_dummy_1 port1
    command = await actor.invoke_mock_command("on nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == 1

    assert switches[0].outlets[0].state == 1

    # switch off nps_dummy_1 port1
    command = await actor.invoke_mock_command("off nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == 0

    assert switches[0].outlets[0].state == 0

    # switch skye.nps port 1
    assert switches[1].name == "skye.nps"
    assert switches[1].outlets[0].name == "skye.pwi"
    assert switches[1].outlets[0].state == -1
    switches[1].outlets[0].state = 0
    assert switches[1].outlets[0].state == 0

    # switch on skye.nps port1
    command = await actor.invoke_mock_command("on skye.nps 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["skye.nps"]["skye.pwi"]["state"] == 1
    assert switches[1].outlets[0].state == 1

    # switch off skye.nps port1
    command = await actor.invoke_mock_command("off skye.nps 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["skye.nps"]["skye.pwi"]["state"] == 0
    assert switches[1].outlets[0].state == 0


@pytest.mark.asyncio
async def test_status_already_on(switches, actor: NpsActor):
    assert actor

    assert switches[0].name == "nps_dummy_1"
    assert switches[0].outlets[0].name == "port1"
    assert switches[0].outlets[0].state == -1
    switches[0].outlets[0].state = 0
    assert switches[0].outlets[0].state == 0

    # switch on nps_dummy_1 port1
    command = await actor.invoke_mock_command("on nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == 1

    # switch on nps_dummy_1 port1
    command = await actor.invoke_mock_command("on nps_dummy_1 1")
    await command
    assert command.status.did_fail


@pytest.mark.asyncio
async def test_status_already_off(switches, actor: NpsActor):
    assert actor
    assert switches[0].name == "nps_dummy_1"
    assert switches[0].outlets[0].name == "port1"
    assert switches[0].outlets[0].state == -1
    switches[0].outlets[0].state = 0
    assert switches[0].outlets[0].state == 0

    # switch on nps_dummy_1 port1
    command = await actor.invoke_mock_command("on nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == 1

    # switch off nps_dummy_1 port1
    command = await actor.invoke_mock_command("off nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    assert len(command.replies) == 4
    assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == 0

    # switch off nps_dummy_1 port1
    command = await actor.invoke_mock_command("off nps_dummy_1 1")
    await command
    assert command.status.did_fail


@pytest.mark.asyncio
async def test_on_fail(switches, actor: NpsActor):
    assert actor
    assert switches[0].name == "nps_dummy_1"
    assert switches[0].outlets[0].name == "port1"
    assert switches[0].outlets[0].state == -1

    # switch on nps_dummy_1 port1
    command = await actor.invoke_mock_command("on nps_dummy_1 1")
    await command
    assert command.status.did_fail


@pytest.mark.asyncio
async def test_off_fail(switches, actor: NpsActor):
    assert actor
    assert switches[0].name == "nps_dummy_1"
    assert switches[0].outlets[0].name == "port1"
    assert switches[0].outlets[0].state == -1

    # switch on nps_dummy_1 port1
    command = await actor.invoke_mock_command("off nps_dummy_1 1")
    await command
    assert command.status.did_fail


@pytest.mark.asyncio
async def test_status_off_after(switches, actor: NpsActor):
    assert actor
    assert switches[0].name == "nps_dummy_1"
    assert switches[0].outlets[0].name == "port1"
    assert switches[0].outlets[0].state == -1
    switches[0].outlets[0].state = 0
    assert switches[0].outlets[0].state == 0

    # switch on nps_dummy_1 port1
    status = []

    status.append(asyncio.create_task(actor.invoke_mock_command("on nps_dummy_1 1 3")))
    status.append(asyncio.create_task(say_after(0.2, actor)))

    status_result = await asyncio.gather(*status)

    assert (
        status_result[1].replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"]
        == 1  # noqa: W503
    )

    await asyncio.sleep(2)

    command = await actor.invoke_mock_command("status nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    assert command.replies[-2].message["status"]["nps_dummy_1"]["port1"]["state"] == 0
    assert switches[0].outlets[0].state == 0


async def say_after(delay, actor_mock):
    await asyncio.sleep(delay)
    command = await actor_mock.invoke_mock_command("status nps_dummy_1 1")
    await command
    assert command.status.did_succeed
    return command
