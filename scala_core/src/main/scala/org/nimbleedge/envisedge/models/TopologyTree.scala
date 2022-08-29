package org.nimbleedge.envisedge.models

import java.security.{MessageDigest => MD}
import java.nio.ByteBuffer

    /**
     * A topology tree data structure is a special type of
	  *structure where many connected elements are arranged
	  *like the branches of tree. Here, there can be one
	  *connection between any two connected modes. Because any
	  *two nodes can have only one mutual connection, tree
	  *topologies create a natural parent and child hierarchy.
	  */
sealed abstract class TopologyTree {
	def computeDigest() : Array[Byte]
	val digest : Array[Byte] = computeDigest()
	override val hashCode : Int = ByteBuffer.wrap(digest.slice(0,4)).getInt

    /**
	  * According to hash function, two same Sets will always have
	  * the same hashcode instead of computing hashcode separately
	  * for the sets, we use their internal one.
	  */
	def hash(baseName: String, args: Set[TopologyTree]): Array[Byte] = {
		val md = MD.getInstance("SHA-256")
		md.reset()
		md.update(baseName.getBytes("UTF-8"))

		// Two Same Sets will always have the same hashcode
		// Instead of computing hashcode separately for the sets,
		// We use their internal one.
		md.update(ByteBuffer.allocate(4).putInt(args.hashCode()).array())

		md.digest()
	}

	override def equals(identifier_val: Any): Boolean = {
		identifier_val match {
			case i : TopologyTree => hashCode == identifier_val.hashCode && MD.isEqual(digest, i.digest)
			case _ => false
		}
	}
}

// Creating Leaf and Node separately for keeping the distinction between Trainers
// and Orchestrators + Aggregators

// Leaf will always be a TrainerIdentifier
    /**
	  * Creating Leaf and Node separately for keeping the
	  * distinction between Trainers and Orchestrators +
	  * Aggregators. Leaf will be always identified as
	  * TrainerIdentifier.
	  */
case class Leaf(value: TrainerIdentifier) extends TopologyTree {
	override def toString(): String = value.name()

	override def computeDigest(): Array[Byte] = hash("_Leaf" + value.name(), Set.empty)
}

// Node can be only OrchestratorIdentifier or AggregatorIdentifier
// It should have more that one children

   /**
	  * Here, node can always be either a OrchestratorIdentifier
	  * or AggregatorIdentifier as left and right child and it
	  * should have more than one children.
	  */
case class Node(value: Either[OrchestratorIdentifier, AggregatorIdentifier], children: Set[TopologyTree]) extends TopologyTree {
	override def toString(): String = {
		val node_value : String = value match {
			case Left(x) => x.name()
			case Right(x) => x.name()
		}
		node_value + children.mkString("(", ", ", ")")
	}

	override def computeDigest(): Array[Byte] = {
		val node_value : String = value match {
			case Left(x) => "_Node_Orc" + x.name()
			case Right(x) => "_Node_Agg" + x.name()
		}
		hash(node_value, children)
	}
}