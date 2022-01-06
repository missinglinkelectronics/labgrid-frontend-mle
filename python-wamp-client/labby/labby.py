"""
A wamp client which registers a rpc function
"""
from typing import Callable, Dict, List, Optional
from time import sleep

import logging
import asyncio
import asyncio.log
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import autobahn.wamp.exception as wexception

import labby.rpc as rpc
from .rpc import RPC
from .router import Router
from .labby_types import PlaceKey

LOADED_RPC_FUNCTIONS: Dict[str, RPC] = {}
ACQUIRED_PLACES: List[PlaceKey] = []
CALLBACK_REF: Optional[ApplicationSession] = None

def get_context_callback():
    """
    If context takes longer to create, prevent Context to be None in Crossbar router context
    """
    return globals()["CALLBACK_REF"]


def register_rpc(func_key: str, endpoint: str, func: Callable) -> None:
    """
    Short hand to inline RPC function registration
    """
    assert not func_key is None
    assert not endpoint is None
    assert not func is None
    globals()["LOADED_RPC_FUNCTIONS"][func_key] = RPC(
        endpoint=endpoint, func=func)


def load_rpc(func_key: str):
    """
    Short hand to retrieve loaded RPCs
    """
    assert not func_key is None
    assert func_key in globals()["LOADED_RPC_FUNCTIONS"]
    return globals()["LOADED_RPC_FUNCTIONS"][func_key]


def get_acquired_places() -> List[PlaceKey]:
    return globals()["ACQUIRED_PLACES"]


class LabbyClient(ApplicationSession):
    """
    Specializes Application Session to handle Communication specifically with the labgrid-frontend and the labgrid coordinator
    """

    def __init__(self, config: None):
        globals()["CALLBACK_REF"] = self
        self.resources = {}
        self.places = {}
        super().__init__(config=config)

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm, ['ticket'], "public")

    def onChallenge(self, challenge):
        self.log.info("Authencticating.")
        if challenge.method == 'ticket':
            return ""
        else:
            self.log.error(
                "Only Ticket authentication enabled, atm. Aborting...")
            raise NotImplementedError(
                "Only Ticket authentication enabled, atm")

    def onJoin(self, details):
        self.log.info("Joined Coordinator Session.")
        self.subscribe(self.onPlaceChanged, u"org.labgrid.coordinator.place_changed")
        self.subscribe(self.onResourceChanged, u"org.labgrid.coordinator.resource_changed")

    def onLeave(self, details):
        self.log.info("Coordinator session disconnected.")
        self.disconnect()

    def onPlaceChanged(self, place_name, place, *args):
        self.log.info(f"Changed place {place_name}.")
        print(place)
        self.places[place_name] = place

    def onResourceChanged(self, *args):
        self.log.info("Changed resource.")
        pass


class RouterInterface(ApplicationSession):

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm)

    def register(self, func_key: str, *args, **kwargs):
        """
        Register functions from RPC store from key, overrides ApplicationSession::register
        """
        callback: RPC = load_rpc(func_key)
        endpoint = callback.endpoint
        func = callback.bind(get_context_callback, *args, **kwargs)
        self.log.info(f"Registered function for endpoint {endpoint}.")
        super().register(func, endpoint)

    def onJoin(self, details):
        self.log.info("Joined Frontend Session.")
        try:
            self.register("places")
            self.register("resource",    'cup')
            self.register("power_state", 'cup')
            self.register("acquire",     'cup')
            self.register("release",     'cup')
            self.register("info")
        except wexception.Error as err:
            self.log.error(
                f"Could not register procedure: {err}.\n{err.with_traceback(None)}")

    def onLeave(self, details):
        self.log.info("Session disconnected.")
        self.disconnect()


def run_router(url: str, realm: str):
    """
    Connect to labgrid coordinator and start local crossbar router
    """
    globals()["LOADED_RPC_FUNCTIONS"] = {}
    globals()["ACQUIRED_PLACES"] = {}

    register_rpc(func_key="places",
                 endpoint="localhost.places", func=rpc.places)
    register_rpc(func_key="resource",
                 endpoint="localhost.resource", func=rpc.resource)
    register_rpc(func_key="power_state",
                 endpoint="localhost.power_state", func=rpc.power_state)
    register_rpc(func_key="acquire",
                 endpoint="localhost.acquire", func=rpc.acquire)
    register_rpc(func_key="release",
                 endpoint="localhost.release", func=rpc.acquire)
    register_rpc(func_key="info", endpoint="localhost.info", func=rpc.info)

    logging.basicConfig(
        level="DEBUG", format="%(asctime)s [%(name)s][%(levelname)s] %(message)s")
    labby_runner = ApplicationRunner(url=url, realm=realm, extra=None)
    labby_coro = labby_runner.run(LabbyClient, start_loop=False)
    frontend_runner = ApplicationRunner(
        url='ws://localhost:8083/ws', realm='frontend', extra=None)
    frontend_coro = frontend_runner.run(RouterInterface, start_loop=False)

    asyncio.log.logger.info("Starting Frontend Router")
    router = Router("labby/router/.crossbar")
    sleep(4)
    loop = asyncio.get_event_loop()
    try:
        asyncio.log.logger.info("Connecting to %s on realm '%s'", url, realm)
        loop.run_until_complete(labby_coro)
        loop.run_until_complete(frontend_coro)
        loop.run_forever()
    except ConnectionRefusedError as err:
        asyncio.log.logger.error(err.strerror)
    except KeyboardInterrupt:
        pass
    finally:
        frontend_coro.close()
        labby_coro.close()
        asyncio.get_event_loop().close()
        router.stop()
