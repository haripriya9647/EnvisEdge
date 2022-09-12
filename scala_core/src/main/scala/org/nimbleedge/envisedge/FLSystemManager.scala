package org.nimbleedge.envisedge

import models._
import scala.collection.mutable.{Map => MutableMap}

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop

  /**
    *Using the object of FLSystemManager, we create actors
    *and requests actor references from an orchestrator, then
    *registers the orchestrator. A similar process applies
    *to aggregators and trainers, where they are first requested,
    *and then registered. An Orchestrator starts the cycle as soon
    *as it terminates by requesting a real-time graph.
    */
object FLSystemManager {
    def apply(): Behavior[Command] =
        Behaviors.setup[Command](new FLSystemManager(_))

    sealed trait Command

    // Creating + Getting the actor references by requesting the Orchestrator
    final case class RequestOrchestrator(requestId: Long, orcId: OrchestratorIdentifier, replyTo: ActorRef[OrchestratorRegistered])
        extends FLSystemManager.Command

    // Registering the Orchestrator
    final case class OrchestratorRegistered(requestId: Long, actor: ActorRef[Orchestrator.Command])

    // Requesting the Aggregator
    final case class RequestAggregator(requestId: Long, aggId: AggregatorIdentifier, replyTo: ActorRef[AggregatorRegistered])
        extends FLSystemManager.Command
        with Orchestrator.Command
        with Aggregator.Command

    //Registering the Aggregator
    final case class AggregatorRegistered(requestId: Long, actor: ActorRef[Aggregator.Command])

    // Requesting the trainer
    final case class RequestTrainer(requestId: Long, traId: TrainerIdentifier, replyTo: ActorRef[TrainerRegistered])
        extends FLSystemManager.Command
        with Orchestrator.Command
        with Aggregator.Command

    // Registering the trainer
    final case class TrainerRegistered(requestId: Long, actor: ActorRef[Trainer.Command])

    // In case of an Orchestrator Termination
    private final case class OrchestratorTerminated(actor: ActorRef[Orchestrator.Command], orcId: OrchestratorIdentifier)
        extends FLSystemManager.Command

    // Requesting RealTimeGraph
    final case class RequestRealTimeGraph(requestId: Long, entity: Either[OrchestratorIdentifier, AggregatorIdentifier], replyTo: ActorRef[RespondRealTimeGraph])
        extends FLSystemManager.Command
        with Orchestrator.Command
        with Aggregator.Command

    // Response of Real time graph
    final case class RespondRealTimeGraph(requestId: Long, realTimeGraph: TopologyTree)

    // Start cycle
    // TODO
    final case class StartCycle(requestId: Long, replyTo: ActorRef[RespondModel]) extends FLSystemManager.Command
    final case class RespondModel(requestId: Long)

    // TODO
    // Add more messages
}

    /**
      *The FL SystemManager is the top level actor of
      *the FL System and it consists of three entities named
      *Orchestrator, Aggregator and Trainer.It consists of
      *a tree like structure where orchestrator is the root
      *node following with aggregator as an intermediate
      *between orchestrator and trainer.An aggregator
      *can have trainer and other aggregators as children.
      *Implementation of FL SystemManager starts here.
       */
class FLSystemManager(context: ActorContext[FLSystemManager.Command]) extends AbstractBehavior[FLSystemManager.Command](context) {
    import FLSystemManager._

    // TODO
    // Topology ??
    // State Information
    var orcIdToRef : MutableMap[OrchestratorIdentifier, ActorRef[Orchestrator.Command]] = MutableMap.empty

    context.log.info("FLSystemManager Started")

    //
    private def getOrchestratorRef(orcId: OrchestratorIdentifier): ActorRef[Orchestrator.Command] = {
        orcIdToRef.get(orcId) match {
            case Some(actorRef) =>
                actorRef
            case None =>
                context.log.info("Creating new orchestrator actor for {}", orcId.name())
                val actorRef = context.spawn(Orchestrator(orcId), s"orchestrator-${orcId.name()}")
                context.watchWith(actorRef, OrchestratorTerminated(actorRef, orcId))
                orcIdToRef += orcId -> actorRef
                actorRef
        }
    }

    override def onMessage(msg: Command): Behavior[Command] =
        msg match {
            // Request for Orchestrator Id
            case RequestOrchestrator(requestId, orcId, replyTo) =>
                val actorRef = getOrchestratorRef(orcId)
                replyTo ! OrchestratorRegistered(requestId, actorRef)
                this
            // request for aggregator Id
            case trackMsg @ RequestAggregator(requestId, aggId, replyTo) =>
                val orcId = aggId.getOrchestrator()

                val orchestratorRef = getOrchestratorRef(orcId)
                orchestratorRef ! trackMsg
                this
            // Request for trainer Id
            case trackMsg @ RequestTrainer(requestId, traId, replyTo) =>
                val orcId = traId.getOrchestrator()

                val orchestratorRef = getOrchestratorRef(orcId)
                orchestratorRef ! trackMsg
                this
            // Request for Real time graph
            case trackMsg @ RequestRealTimeGraph(requestId, entity, replyTo) =>
                val orcId = entity match {
                    case Left(x) => x
                    case Right(x) => x.getOrchestrator()
                }

            // If the requested orchestrator id matches with the actor reference then it tracks the message and requests for a real time graph else it shows error as the orchestrator id doesn't exists.
                orcIdToRef.get(orcId) match {
                    case Some(actorRef) =>
                        actorRef ! trackMsg
                    case None =>
                        context.log.info("Orchestrator with id {} does not exist, can't request realTimeGraph", orcId.name())
                }
                this

            case StartCycle(requestId, replyTo) =>
                // TODO
                this
            // Termination of Orchestrator
            case OrchestratorTerminated(actor, orcId) =>
                context.log.info("Orchestrator with id {} has been terminated", orcId.name())
                // TODO
                this
        }
       // If signal received then then FL system manager stops its process
    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("FLSystemManager Stopped")
            this
    }
}